from soldat_extmod_api.graphics_helper.gui_addon import (
    Button, 
    BUTTON_DEFAULT_COLOR, 
    BUTTON_HOVER_DEFAULT_COLOR, 
    BUTTON_PRESSED_DEFAULT_COLOR
)
from soldat_extmod_api.mod_api import ModAPI, Event, Vector2D, FontStyle
from soldat_extmod_api.graphics_helper.color import Color

from soldat_extmod_api.event_dispatcher import VK_KEYCODE, KeyInfo

from typing import Callable

MODIFIER_TO_VK = {
    'lctrl': VK_KEYCODE.VK_LCONTROL.value,   # 0xA2
    'rctrl': VK_KEYCODE.VK_RCONTROL.value,   # 0xA3
    'lshift': VK_KEYCODE.VK_LSHIFT.value,    # 0xA0
    'rshift': VK_KEYCODE.VK_RSHIFT.value,    # 0xA1
    'lalt': VK_KEYCODE.VK_LMENU.value,       # 0xA4
    'ralt': VK_KEYCODE.VK_RMENU.value,       # 0xA5
}

VK_TO_MODIFIER = {vk: name for name, vk in MODIFIER_TO_VK.items()}


class KeybindButton(Button):
    def __init__(self, mod_api: ModAPI, parent, padding_x, padding_y, callback: Callable[[bool], None]):
        self.api = mod_api
        self.key_display_back = self.api.create_interface_image(
            "graphics/keybind_text_back.png",
            color=Color.from_hex("7be75f7f"),
            scale=Vector2D(0.5, 0.5)
        )

        self.key_display_text = self.api.create_interface_text(
            "",
            Vector2D.zero(),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.5, 1.0),
            FontStyle.FONT_SMALLEST,
            0.5
        )

        self.button_text = self.api.create_interface_text(
            "Edit keybind",
            Vector2D.zero(),
            Color.from_hex("000000ff"),
            Color.from_hex("ffffffff"),
            1.0,
            Vector2D(0.35, 0.7),
            FontStyle.FONT_SMALL_BOLD,
            0.35
        )
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "graphics/keybind_button.png",
                scale=Vector2D(0.5, 0.5)
            ), 
            True
        )
        self.recording = False
        self.callback = callback
        self.image.set_color(BUTTON_DEFAULT_COLOR)
        self.api.subscribe_event(self.on_any_key_up, Event.KEYBOARD_KEYUP)
        self.api.subscribe_event(self.on_any_key_up, Event.MOUSE_KEYUP)
        self.hotkey = {}
        self.prevent_mouse_click_recording = True

    def on_mouse_release(self, position):
        if self.contains_point(position):
            self.recording ^= True
            self.prevent_mouse_click_recording = True
            self.switch_state()
            self.image.set_color(BUTTON_DEFAULT_COLOR)

    def switch_state(self):
        self.callback(self.recording)
        text = "Recording key" if self.recording else "Edit keybind"
        self.button_text.set_text(text)

    def on_click(self, position):
        if self.contains_point(position):
            self.image.set_color(BUTTON_PRESSED_DEFAULT_COLOR)

    def on_cursor_enter(self):
        self.image.set_color(BUTTON_HOVER_DEFAULT_COLOR)

    def on_cursor_exit(self):
        self.image.set_color(BUTTON_DEFAULT_COLOR)

    def set_pos(self, pos):
        super().set_pos(pos)
        self.key_display_back.set_pos(self.corner_top_left - Vector2D(35.0, -1.0))
        self.key_display_text.set_pos(self.corner_top_left - Vector2D(35.0, -5.0))
        self.button_text.set_pos(self.corner_top_left + Vector2D(1.0, 7.0))

    def hide(self):
        self.unsubscribe()
        self.api.unsubscribe_event(self.on_any_key_up, Event.KEYBOARD_KEYUP)
        self.api.unsubscribe_event(self.on_any_key_up, Event.MOUSE_KEYUP)
        self.image.hide()
        self.key_display_back.hide()
        self.key_display_text.hide()
        self.button_text.hide()

    def show(self):
        self.subscribe()
        self.api.subscribe_event(self.on_any_key_up, Event.KEYBOARD_KEYUP)
        self.api.subscribe_event(self.on_any_key_up, Event.MOUSE_KEYUP)
        self.image.show()
        self.key_display_back.show()
        self.key_display_text.show()
        self.button_text.show()

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.key_display_back.destroy()

    def on_any_key_up(self, key: KeyInfo):
        if self.prevent_mouse_click_recording and key.vk_code == VK_KEYCODE.VK_LBUTTON.value:
            self.prevent_mouse_click_recording = False
            return
        if key.vk_code in (VK_KEYCODE.VK_LCONTROL.value, VK_KEYCODE.VK_CONTROL.value):
            return

        if self.recording:
            filtered_mods = [m for m in key.modifiers if m != 'lctrl']

            mod_str = " + ".join(filtered_mods) + (" + " if filtered_mods else "")
            key_text = mod_str + (key.char.upper() if key.char else key.get_key_name())
            self.key_display_text.set_text(key_text.upper())

            modifier_vk_codes = [MODIFIER_TO_VK[m] for m in filtered_mods if m in MODIFIER_TO_VK]
            saved_hotkey = {
                'main_vk': key.vk_code,
                'modifiers': modifier_vk_codes,
            }

            self.hotkey = saved_hotkey

            self.recording = False
            self.switch_state()
