from soldat_extmod_api.interprocess_utils.kernel_wrapper import GetKeyState
from soldat_extmod_api.event_dispatcher import KeyInfo, VK_KEYCODE
from ui.edit_keybind_button import MODIFIER_TO_VK, VK_TO_MODIFIER
from outofbounds_event_provider import OutOfBoundsEventProvider
from ui.offmap_hotkey_settings import OffmapHotkeySettings
from soldat_extmod_api.mod_api import ModAPI, Event
from nonspec_camera_controls import CameraControls
from screen_shake_patch import ScreenShakePatch
from outline_provider import OutlineProvider
from ui.circular_menu import CircularMenu
from offmap_hotkey import OffmapHotkey
from ui.config_ui import ConfigUI
from poly_type import PolyType

import logging
import time
import json
import sys
import os

MAINTICKCOUNTER_PTR = 0x005E3C7C
MAX_TICK = 0xFFFFFFFF


class ModMain:
    def __init__(self) -> None:
        self.api = ModAPI()
        if self.api.soldat_bridge.executable_hash != 1802620099:
            print("Unsupported version for mod, exiting...")
            sys.exit(1)

        self.ensure_default_configs()
        with open("config.json", "r") as f:
            self.config: dict[str, str] = json.load(f)
        self.offmap_hotkey = self.load_hotkey()
        self.screen_shake_patch = ScreenShakePatch(self.api)
        self.screen_shake_patch.remove_patch()
        self.offmap_hotkey_active = False
        self.camera_controls = CameraControls(self.api)
        self.maintickcounter_addr = int.from_bytes(
            self.api.soldat_bridge.read(MAINTICKCOUNTER_PTR, 4), 
            "little"
        )
        self.map_name_len_addr = self.api.addresses["current_map_name_length"]
        self.map_name_addr = self.api.addresses["current_map_name"]
        self.api.event_dispatcher.map_manager = self
        self.api.subscribe_event(self.on_map_change, Event.MAP_CHANGE)
        self.api.subscribe_event(self.on_dx_ready, Event.DIRECTX_READY)
        self.api.subscribe_event(self.on_dx_not_ready, Event.DIRECTX_NOT_READY)
        self.api.subscribe_event(self.on_lcontrol_down, Event.LCONTROL_DOWN)
        self.api.subscribe_event(self.on_lcontrol_up, Event.LCONTROL_UP)
        self.api.subscribe_event(self.on_di_not_ready, Event.DINPUT_NOTREADY)
        self.api.subscribe_event(self.on_di_ready, Event.DINPUT_READY)
        self.api.subscribe_event(self.on_any_key_up, Event.KEYBOARD_KEYUP)
        self.api.subscribe_event(self.on_any_key_up, Event.MOUSE_KEYUP)
        self.outline_provider = OutlineProvider(self.config, self.api)
        self.api.subscribe_event(self.outline_provider.update_wireframe, Event.DIRECTX_READY)
        self.freeze_cam = False
        self.circular_menu: None | CircularMenu = None
        self.game_focused = False
        with open("menu_states.json", "r") as f:
            self.menu_states = json.load(f)
        self.own_player = self.api.get_player(self.api.get_own_id())
        self.oob_event_provider = OutOfBoundsEventProvider(self.api, self.own_player.tsprite_object_addr)
        self.oob_event_provider.patch()
        self.offmap_hkey = OffmapHotkey(self.api, self.camera_controls, self.oob_event_provider)

    def main_loop(self):
        missed_tick_total = 0
        self.last_tick = self.get_ticks()
        while True:
            try:
                if self.get_dx_state():
                    cur_tick = self.get_ticks()
                    if cur_tick != self.last_tick:
                        if cur_tick > self.last_tick:
                            ticks_missed = cur_tick - self.last_tick
                        else:
                            ticks_missed = (MAX_TICK - self.last_tick) + cur_tick + 1
                        if ticks_missed > 1:
                            logging.warning(f"Missed {ticks_missed - 1} ticks")
                            missed_tick_total += (ticks_missed - 1)
                        self.api.tick_event_dispatcher()
                        self.on_every_tick(cur_tick)
                    self.last_tick = cur_tick
                else:
                    self.api.tick_event_dispatcher()
                if self.circular_menu:
                    self.circular_menu.update_transitions()
                    time.sleep(0.00001)
            except KeyboardInterrupt:
                break
        logging.info(f"Total missed ticks: {missed_tick_total}")

# ================= EVENT HANDLERS ================= #

    def on_map_change(self, _) -> None:
        self.outline_provider.update_wireframe()

    def on_every_tick(self, tick: int):
        if self.ui and not self.ui.hidden:
            self.ui.brightness_container.brightness_slider.knob.update_percentage(
                self.ui.brightness_container.brightness_slider.knob.index
            )
            self.ui.transparency_container.transparency_slider.knob.update_percentage(
                self.ui.transparency_container.transparency_slider.knob.index
            )
        if self.offmap_hotkey_active:
            self.offmap_hkey.tick()

    def on_dx_ready(self):
        self.ui = ConfigUI(self.api, 0, 0, self.config, self.on_save)
        self.circular_menu = CircularMenu(self.api, self.api.get_gui_frame())
        self.circular_menu.outline_toggle_button.toggled_action_callback(self.outline_provider.show)
        self.circular_menu.outline_toggle_button.set_action_callback(self.outline_provider.hide)
        self.circular_menu.outline_settings_button.set_action_callback(self.ui.show)
        self.circular_menu.mode_cycle_button.set_callback(self.set_wireframe_mode)
        self.circular_menu.scenery_toggle_button.set_action_callback(self.disable_props)
        self.circular_menu.scenery_toggle_button.toggled_action_callback(self.enable_props)
        self.circular_menu.outline_toggle_button.toggled = self.menu_states["outline_toggled"]
        self.circular_menu.outline_toggle_button.toggle()
        if not self.menu_states["dark_mode"]: self.circular_menu.toggle_color_mode()
        self.circular_menu.mode_cycle_button.state = self.menu_states["outline_mode"]
        self.circular_menu.mode_cycle_button.apply_mode()
        self.circular_menu.scenery_toggle_button.toggled = self.menu_states["scenery_toggled"]
        self.circular_menu.scenery_toggle_button.toggle()
        self.hotkey_settings = OffmapHotkeySettings(
            self.api, 0, 0,
            self.screen_shake_callback,
            self.key_bind_save_callback,
            self.set_camera_pinning_mode,
            self.offmap_hotkey_state_callback
        )
        if self.offmap_hotkey:
            main_vk = self.offmap_hotkey['main_vk']
            mod_vks = self.offmap_hotkey.get('modifiers', [])

            mod_names = [VK_TO_MODIFIER[vk] for vk in mod_vks if vk in VK_TO_MODIFIER]

            mod_str = " + ".join(mod_names) + (" + " if mod_names else "")

            if (0x30 <= main_vk <= 0x39) or (0x41 <= main_vk <= 0x5A):
                main_name = chr(main_vk).upper()
            else:
                main_name = next((m.name[3:].capitalize() for m in VK_KEYCODE if m.value == main_vk), f"VK_{main_vk:02X}")

            key_text = (mod_str + main_name).upper()
        else:
            key_text = "NOT SET"

        self.hotkey_settings.rows[0].keybind_button.key_display_text.set_text(key_text)
        self.circular_menu.offmap_settings_button.set_action_callback(self.hotkey_settings.show)
        self.api.enable_drawing()

    def on_dx_not_ready(self):
        self.api.disable_drawing()
        self.menu_states["dark_mode"] = self.circular_menu.dark_mode
        self.menu_states["outline_toggled"] = self.circular_menu.outline_toggle_button.toggled
        self.menu_states["outline_mode"] = self.circular_menu.mode_cycle_button.state
        self.menu_states["scenery_toggled"] = self.circular_menu.scenery_toggle_button.toggled
        self.circular_menu.destroy()
        self.ui.destroy()
        self.hotkey_settings.destroy()
        self.ui = None
        self.circular_menu = None
        self.hotkey_settings = None

    def on_save(self, config: dict[str, str]):
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        self.config = config.copy()
        self.outline_provider.config = config.copy()
        self.outline_provider.update_wireframe()

    def on_lcontrol_down(self):
        if self.game_focused and self.api.get_player(self.api.get_own_id()).team == 5:
            if not self.freeze_cam:
                self.api.take_cursor_controls()
                self.api.take_camera_controls()
                self.freeze_cam = True

    def on_lcontrol_up(self):
        if self.game_focused and self.api.get_player(self.api.get_own_id()).team == 5:
            self.api.restore_cursor_controls()
            self.api.restore_camera_controls()
            self.freeze_cam = False

    def disable_props(self):
        self.api.disable_props0_layer()
        self.api.disable_props1_layer()
        self.api.disable_props2_layer()

    def enable_props(self):
        self.api.enable_props0_layer()
        self.api.enable_props1_layer()
        self.api.enable_props2_layer()

    def set_wireframe_mode(self, mode: int):
        match mode:
            case 0:
                self.outline_provider.outline_mode = "fill"
                if self.outline_provider.visible:
                    self.api.disable_polygon_layer()
                    self.api.disable_backpoly_layer()
                self.api.set_polygon_mode("fill")
            case 1:
                self.outline_provider.outline_mode = "line"
                self.api.enable_polygon_layer()
                self.api.enable_backpoly_layer()
                self.api.set_polygon_mode("line") 
            case 2:
                self.outline_provider.outline_mode = "outline_only"
                self.api.set_polygon_mode("line")
                if self.outline_provider.visible:
                    self.api.disable_polygon_layer()
                    self.api.disable_backpoly_layer()

    def on_di_ready(self):
        self.game_focused = True

    def on_di_not_ready(self):
        self.game_focused = False
        self.api.restore_cursor_controls()
        self.api.restore_camera_controls()
        self.freeze_cam = False

    def screen_shake_callback(self, checked: bool):
        if checked:
            self.screen_shake_patch.apply_patch()
        else:
            self.screen_shake_patch.remove_patch()

    def key_bind_save_callback(self, state: bool):
        if state == False:
            hotkey = self.hotkey_settings.rows[0].keybind_button.hotkey
            if hotkey:
                self.save_hotkey(hotkey)
                self.offmap_hotkey = hotkey

    def on_any_key_up(self, key_info: KeyInfo):
        if not self.game_focused or not self.offmap_hotkey_active:
            return
        if self.matches_saved_hotkey(key_info):
            self.offmap_hkey.on_offmap_hotkey_pressed()

    def set_camera_pinning_mode(self, mode: bool):
        self.offmap_hkey.use_camera_pinning = mode

    def offmap_hotkey_state_callback(self, state: bool):
        self.offmap_hotkey_active = state

    def matches_saved_hotkey(self, key_info: KeyInfo):
        if key_info.vk_code != self.offmap_hotkey['main_vk']:
            return False

        for mod_vk in self.offmap_hotkey['modifiers']:
            if not (GetKeyState(mod_vk) & 0x8000):
                return False

        all_modifier_vks = set(MODIFIER_TO_VK.values())
        pressed_modifiers = {vk for vk in all_modifier_vks if GetKeyState(vk) & 0x8000}
        if pressed_modifiers != set(self.offmap_hotkey['modifiers']):
            return False

        return True

# ================= HELPERS ================= #

    def get_dx_state(self) -> bool:
        return bool.from_bytes(
            self.api.soldat_bridge.read(
                self.api.addresses["dxready"], 1
            )
        )

    @property
    def current_map_name(self) -> str:
        name_length = int.from_bytes(
            self.api.soldat_bridge.read(self.map_name_len_addr, 1), "little"
        )
        if name_length > 0:
            return self.api.soldat_bridge.read(
                self.map_name_addr, name_length
            ).decode("utf-8")
        else:
            while name_length == 0:
                name_length = int.from_bytes(
                    self.api.soldat_bridge.read(self.map_name_len_addr, 1), "little"
                )
            return self.api.soldat_bridge.read(
                self.map_name_addr, name_length
            ).decode("utf-8")

    def get_ticks(self):
        cur_tick = self.api.soldat_bridge.read(self.maintickcounter_addr, 4)
        cur_tick = int.from_bytes(cur_tick, "little")
        return cur_tick

    def save_hotkey(self, hotkey):
        with open("hotkey.json", "w") as f:
            json.dump(hotkey, f)

    def load_hotkey(self):
        with open("hotkey.json", "r") as f:
            return json.load(f)

    def ensure_default_configs(self):
        if not os.path.exists("config.json"):
            default_colors = {member.name: "ffffffff" for member in PolyType}
            with open("config.json", "w") as f:
                json.dump(default_colors, f, indent=4)

        if not os.path.exists("menu_states.json"):
            with open("menu_states.json", "w") as f:
                json.dump({
                    "dark_mode": True,
                    "outline_toggled": False,
                    "outline_mode": 1,
                    "scenery_toggled": True
                },f, indent=4)

        if not os.path.exists("hotkey.json"):
            with open("hotkey.json", "w") as f:
                json.dump({"main_vk": 67, "modifiers": []}, f)


if __name__ == "__main__":
    main = ModMain()
    main.main_loop()
