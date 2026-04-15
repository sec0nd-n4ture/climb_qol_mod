from ui.setting_row import CheckboxSettingRow, EditKeybindSettingRow, SettingRow
from soldat_extmod_api.mod_api import ModAPI, Color, FontStyle, Vector2D
from soldat_extmod_api.graphics_helper.gui_addon import Container
from ui.config_buttons import CloseButton
from typing import Callable

ROW_PADDING_X = 7.0
ROW_PADDING_Y = 5.0
ROW_START_PADDING_Y = 28.0

class OffmapHotkeySettings(Container):
    def __init__(
            self, 
            mod_api: ModAPI, 
            padding_x: float, 
            padding_y: float,
            screen_shake_callback: Callable[[bool], None],
            keybind_callback: Callable[[bool], None],
            camera_pinning_callback: Callable[[bool], None],
            offmap_hotkey_state_callback: Callable[[bool], None],
            freecam_state_callback: Callable[[bool], None]
        ):
        self.title_text = mod_api.create_interface_text(
            "Offmap Hotkey Settings",
            Vector2D.zero(),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.8, 1.6),
            FontStyle.FONT_SMALL_BOLD,
            0.7
        )
        self.api = mod_api
        super().__init__(
            mod_api.get_gui_frame(), 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "graphics/config_ui_back.png",
                scale=Vector2D(0.46, 0.55)
            ), 
            True
        )
        self.close_button = CloseButton(self.api, self, 0, 0, self.hide)
        self.close_button.set_pos(self.corner_top_right - Vector2D(15.0, -2.0))
        self.rows : list[SettingRow] = []
        self.add_row(EditKeybindSettingRow(self, "Set offmap keybind", self.api, keybind_callback))
        self.add_row(CheckboxSettingRow(self, "Use camera pinning", self.api, camera_pinning_callback))
        self.add_row(CheckboxSettingRow(self, "Disable screen shake", self.api, screen_shake_callback))
        self.add_row(CheckboxSettingRow(self, "Enable offmap hotkey", self.api, offmap_hotkey_state_callback))
        self.add_row(CheckboxSettingRow(self, "Enable free cam", self.api, freecam_state_callback))
        self.hidden = False
        self.hide()

    def add_row(self, row: SettingRow):
        if self.rows:
            position = self.rows[-1].corner_bottom_left + Vector2D(0.0, ROW_PADDING_Y)
        else:
            position = row.position.add(Vector2D(ROW_PADDING_X, ROW_START_PADDING_Y))
        row.set_pos(position)
        self.rows.append(row)

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.image.hide()
            self.close_button.hide()
            self.title_text.hide()
            for row in self.rows:
                row.hide()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.image.show()
            self.close_button.show()
            self.title_text.show()
            for row in self.rows:
                row.show()

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.close_button.destroy()
        for row in self.rows:
            row.destroy()

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)
        self.title_text.set_pos(pos + Vector2D(18.0, 9.0))
