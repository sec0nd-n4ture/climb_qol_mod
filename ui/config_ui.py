from ui.slider_container import TransparencySliderContainer, BrightnessSliderContainer
from soldat_extmod_api.mod_api import ModAPI, Color, FontStyle, Vector2D
from soldat_extmod_api.graphics_helper.sm_text import CharacterSize
from ui.config_buttons import CycleButton, CloseButton, SaveButton
from soldat_extmod_api.graphics_helper.gui_addon import Container
from ui.hsv_color_wheel import HSVColorWheel
from poly_type import PolyType
from typing import Callable


class ConfigUI(Container):
    def __init__(
            self, 
            mod_api: ModAPI, 
            padding_x: float, 
            padding_y: float,
            config: dict[str, str],
            save_callback: Callable[[dict[str, str]], None]
        ):
        self.save_callback = save_callback
        self.config = config.copy()
        self.current_poly_type = 0
        self.title_text = mod_api.create_interface_text(
            "Outline Settings",
            Vector2D.zero(),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.8, 1.6),
            FontStyle.FONT_SMALL_BOLD,
            0.8
        )
        cur_poly_type_name = PolyType._value2member_map_[self.current_poly_type].name
        self.poly_type_text_scale = 0.7
        textlenhalf = len(cur_poly_type_name) // 2
        self.text_center_offset = Vector2D(
            (textlenhalf * (CharacterSize.FONT_SMALL_BOLD * self.poly_type_text_scale)) +
            (textlenhalf * (CharacterSize.FONT_SMALL_BOLD_SPACING * self.poly_type_text_scale)),
            0
        )
        self.text_center_offset.y += 8
        self.current_poly_text = mod_api.create_interface_text(
            cur_poly_type_name,
            Vector2D.zero(),
            Color.from_hex(self.config[cur_poly_type_name]),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(self.poly_type_text_scale, self.poly_type_text_scale*2),
            FontStyle.FONT_SMALL_BOLD,
            self.poly_type_text_scale
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
        self.save_action: None | Callable[[], None] = self.on_save

        self.hidden = False
        self.color_wheel = HSVColorWheel(self, 20.0, 23.0, self.api, self.on_color_change)
        self.color_wheel.set_from_rgba(bytes.fromhex(self.config[cur_poly_type_name]))
        self.cycle_button_right = CycleButton(self.api, self, 0, 0, 1, self.cycle_polygon_types)
        self.cycle_button_left = CycleButton(self.api, self, 0, 0, 0, self.cycle_polygon_types)
        self.cycle_button_right.set_pos(self.corner_bottom_right.add(Vector2D(-25.0, 0.0)))
        self.cycle_button_left.set_pos(self.corner_bottom_left.add(Vector2D(8.0, 0.0)))
        self.set_polygon_type_text(cur_poly_type_name)
        self.close_button = CloseButton(self.api, self, 0, 0, self.hide)
        self.close_button.set_pos(self.corner_top_right - Vector2D(15.0, -2.0))
        self.save_button = SaveButton(self.api, self, 0, 0)
        self.save_button.set_pos(self.corner_bottom_left + Vector2D(80.0, 16.0))
        self.save_button.action = self.save_action

        self.brightness_container = BrightnessSliderContainer(
            self.api, self.api.get_gui_frame(), 0, 65.0, self.on_brightness_change
        )

        self.brightness_container.brightness_slider.set_brightness(bytes.fromhex(self.config[cur_poly_type_name]))
        self.brightness_text = mod_api.create_interface_text(
            "Brightness",
            self.brightness_container.position - Vector2D(0.0, 10.0),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.5, 1.0),
            FontStyle.FONT_SMALL_BOLD,
            0.5
        )

        self.transparency_container = TransparencySliderContainer(
            self.api, self.api.get_gui_frame(), 0, 95.0, self.on_alpha_change
        )

        self.transparency_container.transparency_slider.set_alpha(bytes.fromhex(self.config[cur_poly_type_name]))
        self.transparency_text = mod_api.create_interface_text(
            "Transparency",
            self.transparency_container.position - Vector2D(0.0, 10.0),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.5, 1.0),
            FontStyle.FONT_SMALL_BOLD,
            0.5
        )

        self.hide()

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)
        self.title_text.set_pos(pos + Vector2D(35.0, 9.0))

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.image.hide()
            self.title_text.hide()
            self.current_poly_text.hide()
            self.color_wheel.hide()
            self.cycle_button_right.hide()
            self.cycle_button_left.hide()
            self.close_button.hide()
            self.brightness_container.hide()
            self.brightness_text.hide()
            self.transparency_container.hide()
            self.transparency_text.hide()
            self.save_button.hide()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.image.show()
            self.title_text.show()
            self.current_poly_text.show()
            self.color_wheel.show()
            self.cycle_button_right.show()
            self.cycle_button_left.show()
            self.close_button.show()
            self.brightness_container.show()
            self.brightness_text.show()
            self.transparency_container.show()
            self.transparency_text.show()
            self.save_button.show()

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.color_wheel.destroy()
        self.cycle_button_left.destroy()
        self.cycle_button_right.destroy()
        self.close_button.destroy()
        self.brightness_container.destroy()
        self.transparency_container.destroy()
        self.save_button.destroy()

    def on_color_change(self, color: bytes):
        self.current_poly_text.set_text_color(Color.from_bytes(color))

    def on_brightness_change(self, brightness: int):
        value_float = brightness / 255.0
        self.color_wheel.set_value(value_float)

    def on_alpha_change(self, alpha: int):
        self.color_wheel.set_alpha(alpha)

    def on_save(self):
        cur_poly_type_name = PolyType._value2member_map_[self.current_poly_type].name
        self.config[cur_poly_type_name] = self.color_wheel.current_color.hex()
        self.save_callback(self.config)

    def cycle_polygon_types(self, direction: int):
        dir = 1 if direction else -1
        self.current_poly_type = (self.current_poly_type + dir) % len(PolyType._member_map_.keys())
        cur_poly_type_name = PolyType._value2member_map_[self.current_poly_type].name
        self.set_polygon_type_text(cur_poly_type_name)
        cur_color = Color.from_hex(self.config[cur_poly_type_name])
        self.color_wheel.set_from_rgba(cur_color.to_bytes())
        self.brightness_container.brightness_slider.set_brightness(cur_color.to_bytes())
        self.transparency_container.transparency_slider.set_alpha(cur_color.to_bytes())

    def set_polygon_type_text(self, text: str):
        textlenhalf = len(text) // 2
        self.text_center_offset = Vector2D(
            (textlenhalf * (CharacterSize.FONT_SMALL_BOLD * self.poly_type_text_scale)) +
            (textlenhalf * (CharacterSize.FONT_SMALL_BOLD_SPACING * self.poly_type_text_scale)), 
            0
        )
        self.text_center_offset.y += 8

        self.current_poly_text.set_text(text)
        self.current_poly_text.set_pos((self.corner_bottom_left + Vector2D(85.0, 10.0)) - self.text_center_offset)
