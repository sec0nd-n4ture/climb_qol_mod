from soldat_extmod_api.graphics_helper.gui_addon import Container, Checkbox
from soldat_extmod_api.mod_api import ModAPI, Color, FontStyle, Vector2D
from typing import Callable

from ui.edit_keybind_button import KeybindButton


class SettingRow(Container):
    def __init__(self, parent, setting_text: str, mod_api: ModAPI):
        self.setting_text = mod_api.create_interface_text(
            setting_text,
            Vector2D.zero(),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.5, 1.0),
            FontStyle.FONT_SMALL_BOLD,
            0.5
        )
        super().__init__(
            parent, 
            0, 
            0, 
            mod_api.create_interface_image(
                "graphics/setting_row_back.png",
                color=Color("100%", "100%", "100%", "70%"),
                scale=Vector2D(0.46, 0.5)
            ), 
            False
        )
        self.mod_api = mod_api
        self.destroyables = []
        self.hidden = False

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.image.hide()
            self.setting_text.hide()
            return True
        return False

    def show(self):
        if self.hidden:
            self.hidden = False
            self.image.show()
            self.setting_text.show()
            return True
        return False

    def destroy(self):
        self.hide()
        self.image.destroy()
        for destroyable in self.destroyables:
            destroyable.destroy()

    def add_destroyable(self, destroyable):
        self.destroyables.append(destroyable)

    def set_pos(self, pos):
        super().set_pos(pos)
        self.setting_text.set_pos(self.corner_top_left + Vector2D(2.0, 7.0))

class CheckboxSetting(Checkbox):
    def __init__(
            self, 
            parent, 
            mod_api: ModAPI, 
            padding_x: float, 
            padding_y: float, 
            check_callback : Callable[[bool],None]
        ):
        self.mod_api = mod_api
        checkbox_image = self.mod_api.create_interface_image(
            "graphics/checkbox.png", 
            scale=Vector2D(0.5, 0.5)
        )
        super().__init__(self.mod_api, parent, padding_x, padding_y, checkbox_image, False)
        self.unchecked_color = Color.from_hex("1b1b1bff")
        self.checked_color = Color.from_hex("898989ff")
        self.checkbox_outline = self.mod_api.create_interface_image(
            "graphics/checkbox_outline.png", 
            self.position.sub(Vector2D(1, 1)), 
            scale=Vector2D(0.5, 0.5), 
            color=Color.from_hex("ffffffff")
        )
        self.check_callback = check_callback
        self.update_check()

    def set_pos(self, pos):
        super().set_pos(pos)
        if hasattr(self, "checkbox_outline"):
            self.checkbox_outline.set_pos(pos.sub(Vector2D(1, 1)))

    def hide(self):
        self.image.hide()
        self.checkbox_outline.hide()
        self.unsubscribe()

    def show(self):
        self.image.show()
        self.checkbox_outline.show()
        self.subscribe()

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.checkbox_outline.destroy()

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.checked ^= True
            self.update_check()
            self.check_callback(self.checked)

    def update_check(self):
        self.image.set_color(
            self.checked_color if self.checked else self.unchecked_color
        )

class CheckboxSettingRow(SettingRow):
    def __init__(
            self, 
            parent, 
            setting_text, 
            mod_api, 
            check_callback: Callable[[bool],None]
        ):
        super().__init__(parent, setting_text, mod_api)
        self.checkbox_setting = CheckboxSetting(self, mod_api, 0, 0, check_callback)
        self.add_destroyable(self.checkbox_setting)

    def set_pos(self, pos):
        super().set_pos(pos)
        if hasattr(self, "checkbox_setting"):
            self.checkbox_setting.set_pos(self.corner_top_right - Vector2D(15.0, -6.0))

    def hide(self):
        hidden = super().hide()
        if hidden:
            self.checkbox_setting.hide()

    def show(self):
        shown = super().show()
        if shown:
            self.checkbox_setting.show()


class EditKeybindSettingRow(SettingRow):
    def __init__(
            self, 
            parent, 
            setting_text, 
            mod_api, 
            press_callback: Callable[[bool],None]
        ):
        super().__init__(parent, setting_text, mod_api)
        self.keybind_button = KeybindButton(self.mod_api, self, 0, 0, press_callback)
        self.add_destroyable(self.keybind_button)

    def set_pos(self, pos):
        super().set_pos(pos)
        if hasattr(self, "keybind_button"):
            self.keybind_button.set_pos(self.corner_top_right - Vector2D(43.0, -3.0))

    def hide(self):
        hidden = super().hide()
        if hidden:
            self.keybind_button.hide()

    def show(self):
        shown = super().show()
        if shown:
            self.keybind_button.show()
