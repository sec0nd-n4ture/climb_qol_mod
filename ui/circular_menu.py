from soldat_extmod_api.graphics_helper.gui_addon import Container, Interactive, Rectangle, Button, ImageNode
from soldat_extmod_api.mod_api import ModAPI, Frame, Vector2D, BLACK, WHITE, Color
from soldat_extmod_api.graphics_helper.math_utils import lerpf, radians, cos, sin
from soldat_extmod_api.graphics_helper.sm_text import CharacterSize, FontStyle
from typing import Callable
import time


class CircularMenu(Container, Interactive):
    def __init__(self, mod_api: ModAPI, parent: Frame):
        self.mod_api = mod_api
        self.outline_toggle_button = OutlineToggleMenuButton(parent, mod_api)
        self.outline_settings_button = OutlineSettingsMenuButton(mod_api, parent)
        self.mode_cycle_button = OutlineCycleModeMenuButton(parent, mod_api)
        self.scenery_toggle_button = ToggleSceneryMenuButton(parent, mod_api)
        self.offmap_settings_button = OffmapSettingsMenuButton(mod_api, parent)
        self.buttons: list[CircularMenuButton] = [
            self.outline_toggle_button, 
            self.mode_cycle_button,
            self.outline_settings_button,
            self.offmap_settings_button,
            self.scenery_toggle_button
        ]
        image = mod_api.create_interface_image(
            "graphics/rm_logo.png", 
            scale=Vector2D(0.1, 0.1), 
            color=BLACK
        )
        self.light_image = mod_api.create_interface_image(
            "graphics/rm_logo_light.png", 
            scale=Vector2D(0.1, 0.1), 
            color=WHITE
        )
        self.light_image.hide()
        self.max_retraction_offset = 20
        self.max_protraction_offset = 60
        self.buttons_max_retraction_offset = 5
        self.buttons_max_protraction_offset = 60

        self.retracted_position_x_padding = parent.position.x - \
            ((image.get_dimensions.x / 2) * 0.1) + self.max_retraction_offset

        self.retracted_position_y_padding = parent.position.y - \
            ((image.get_dimensions.y / 2) * 0.1) - self.max_protraction_offset

        self.image_height_half = ((image.get_dimensions.y / 2) * 0.1)
        self.image_width_half = ((image.get_dimensions.x / 2) * 0.1)
        super().__init__(
            parent, 
            self.retracted_position_x_padding, 
            self.retracted_position_y_padding, 
            image, 
            True
        )
        Interactive.__init__(self, self.mod_api)
        self.button_center_offset_x = self.image_width_half - \
            (self.outline_toggle_button.image.get_dimensions.x / 2) * self.outline_toggle_button.scale.x

        self.button_center_offset_y = self.image_height_half - \
            (self.outline_toggle_button.image.get_dimensions.y / 2) * self.outline_toggle_button.scale.y

        self.dragging = False
        self.cursor_inside = False
        self.area_trigger_cursor_inside = False
        self.start_position = self.position.x
        self.target_position_x = self.position.x
        self.button_center_x = self.position.x \
            + self.image_width_half - self.button_center_offset_x
        self.target_position_y = self.position.y
        self.target_color = BLACK
        self.update_delay = 0.01
        self.transition_smoothness = 0.1
        self.past_time = 0
        self.area_trigger = Rectangle(
            self.position.sub(Vector2D(65, 30)), 
            self.dimensions, 
            self.scale + Vector2D(0.2, 0.2)
        )
        self.start_angle_rad = radians(210) # left cone
        self.end_angle_rad = radians(140)
        self.calculate_button_positions(initial=True)
        self.hidden = False
        self.dark_mode = True

    def toggle_color_mode(self):
        self.dark_mode ^= True
        color = WHITE if self.dark_mode else BLACK
        for button in self.buttons:
            for colorable in button.colorables:
                colorable.set_color(color)
            button.image.set_color(WHITE if not self.dark_mode else BLACK)
        if not self.dark_mode:
            self.image.hide()
            self.light_image.show()
        else:
            self.image.show()
            self.light_image.hide()

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.unsubscribe()
            self.image.hide()
            self.light_image.hide()
            for button in self.buttons:
                button.hide()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.subscribe()
            if not self.dark_mode:
                self.image.hide()
                self.light_image.show()
            else:
                self.image.show()
                self.light_image.hide()
            for button in self.buttons:
                button.show()
            self.update_transitions()

    def destroy(self):
        self.hide()
        for button in self.buttons:
            button.destroy()
        self.image.destroy()
        self.light_image.destroy()

    def on_hover(self, position: Vector2D):
        is_inside = self.contains_point(position)
        if not self.cursor_inside and is_inside:
            self.cursor_inside = True
            self.on_cursor_enter()
        if self.cursor_inside and not is_inside:
            self.cursor_inside = False

        is_inside = self.area_trigger.contains_point(position)
        if not self.area_trigger_cursor_inside and is_inside:
            self.area_trigger_cursor_inside = True
        if self.area_trigger_cursor_inside and not is_inside:
            self.area_trigger_cursor_inside = False
            self.on_area_trigger_cursor_exit()
        if self.dragging:
            self.target_position_y = position.y - self.image_height_half
    
    def on_click(self, position: Vector2D):
        if not self.dragging and self.contains_point(position):
            self.dragging = True

    def on_mouse_release(self, position: Vector2D):
        if self.dragging:
            self.dragging = False
            self.target_position_y = position.y - self.image_height_half
            self.calculate_button_positions()
            self.on_area_trigger_cursor_exit()
        if self.contains_point(position):
            self.toggle_color_mode()
            self.on_cursor_enter()

    def on_cursor_enter(self):
        self.target_position_x = self.start_position - 30
        self.target_color = WHITE
        for button in self.buttons:
            button.target_position = button.end_position

    def on_area_trigger_cursor_exit(self):
        if not self.dragging:
            self.target_position_x = self.start_position
            self.target_color = BLACK
            for button in self.buttons:
                button.target_position = button.start_position

    def update_transitions(self):
        if self.hidden:
            return
        now = time.perf_counter()
        if now - self.past_time >= self.update_delay:
            self.set_pos(
                Vector2D(
                    lerpf(self.position.x, self.target_position_x, self.transition_smoothness),
                    lerpf(self.position.y, self.target_position_y, self.transition_smoothness)
                )
            )
            self.image.set_color(
                Color.lerp_color(
                    self.image.get_color, 
                    self.target_color, 
                    self.transition_smoothness
                )
            )
            for button in self.buttons:
                button.set_pos(
                    Vector2D(
                        lerpf(button.position.x, button.target_position.x, self.transition_smoothness),
                        lerpf(button.position.y, button.target_position.y, self.transition_smoothness)
                    )
                )
            self.past_time = now

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "area_trigger"):
            self.area_trigger.position = Vector2D(self.area_trigger.position.x, pos.y - 20)
        self.light_image.set_pos(pos)
        super().set_pos(pos)

    def calculate_button_positions(self, initial: bool = False):
        num_points = len(self.buttons)
        for i in range(num_points):
            angle = self.start_angle_rad + (self.end_angle_rad - self.start_angle_rad) * i / (num_points - 1)
            angle_cos = cos(angle)
            angle_sin = sin(angle)
            x = self.button_center_x + self.buttons_max_retraction_offset * angle_cos

            y = self.target_position_y + self.image_height_half \
                - self.button_center_offset_y + self.buttons_max_retraction_offset * angle_sin

            self.buttons[i].start_position = Vector2D(x, y)
            x = self.button_center_x + self.buttons_max_protraction_offset * angle_cos

            y = self.target_position_y + self.image_height_half \
                - self.button_center_offset_y + self.buttons_max_protraction_offset * angle_sin

            self.buttons[i].end_position = Vector2D(x, y)
            if initial: self.buttons[i].target_position = self.buttons[i].start_position

class CircularMenuButton(Button):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent: Frame, 
            icon_image_path: str, 
            tooltip_text: str = "Default tooltip"
        ):
        image = mod_api.create_interface_image(
            "graphics/circle.png", 
            scale=Vector2D(0.15, 0.15), 
            color=BLACK
        )
        self.button_icon = mod_api.create_interface_image(
            icon_image_path, 
            scale=Vector2D(0.35, 0.35)
        )
        self.colorables: list[ImageNode] = []
        self.colorables.append(self.button_icon)
        self.button_icon_half = Vector2D(
            ((self.button_icon.get_dimensions.x / 2) * self.button_icon.get_scale.x) \
                - ((image.get_dimensions.x / 2) * 0.15)
            ,
            ((self.button_icon.get_dimensions.y / 2) * self.button_icon.get_scale.y) \
                - ((image.get_dimensions.y / 2) * 0.15) + 1
        )
        super().__init__(mod_api, parent, 0, 0, image, True)
        self.action: Callable | None = None
        self.start_position = Vector2D.zero()
        self.target_position = Vector2D.zero()
        self.end_position = Vector2D.zero()
        self.tooltip_text_scale = 0.7
        self.tooltip_text = tooltip_text
        self.tooltip_interface_text = mod_api.create_interface_text(
            tooltip_text, 
            self.position, 
            WHITE, 
            BLACK, 
            1, 
            Vector2D(0.7, 1.4), 
            FontStyle.FONT_SMALL_BOLD, 
            self.tooltip_text_scale
        )
        self.tooltip_interface_text.hide()
        tt_textlenhalf = len(self.tooltip_text) // 2
        self.text_center_offset = Vector2D(
            (tt_textlenhalf * (CharacterSize.FONT_SMALL_BOLD * self.tooltip_text_scale)) +
            (tt_textlenhalf * (CharacterSize.FONT_SMALL_BOLD_SPACING * self.tooltip_text_scale)),
            0
        )
        self.text_center_offset.y += 8
        self.hidden = False

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.unsubscribe()
            self.image.hide()
            self.tooltip_interface_text.hide()
            self.button_icon.hide()
            return True
        return False

    def show(self):
        if self.hidden:
            self.hidden = False
            self.subscribe()
            self.image.show()
            self.tooltip_interface_text.show()
            self.button_icon.show()
            return True
        return False

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.button_icon.destroy()

    def set_pos(self, pos: Vector2D):
        self.button_icon.set_pos(pos.sub(self.button_icon_half))
        return super().set_pos(pos)
    
    def on_hover(self, position: Vector2D):
        super().on_hover(position)
        if self.cursor_inside:
            self.tooltip_interface_text.set_pos(position.sub(self.text_center_offset))

    def on_cursor_enter(self):
        self.tooltip_interface_text.show()

    def on_cursor_exit(self):
        self.tooltip_interface_text.hide()

    def set_tooltip_text(self, text: str):
        tt_textlenhalf = len(text) // 2
        self.text_center_offset = Vector2D(
            (tt_textlenhalf * (CharacterSize.FONT_SMALL_BOLD * self.tooltip_text_scale)) +
            (tt_textlenhalf * (CharacterSize.FONT_SMALL_BOLD_SPACING * self.tooltip_text_scale)), 
            0
        )
        self.text_center_offset.y += 8

        self.tooltip_interface_text.set_text(text)
        self.tooltip_text = text

    def set_action_callback(self, callback: Callable):
        self.action = callback

class OutlineToggleMenuButton(CircularMenuButton):
    def __init__(self, parent: Frame, mod_api: ModAPI):
        super().__init__(mod_api, parent, "graphics/fa-eye-solid.png", "Hide polygon outline")
        self.button_icon_toggled = mod_api.create_interface_image(
            "graphics/fa-eye-slash-solid.png", 
            scale=Vector2D(0.35, 0.35)
        )
        self.colorables.append(self.button_icon_toggled)
        self.button_icon_toggled.hide()
        self.toggled = False
        self.toggled_action = None

    def hide(self):
        hidden = super().hide()
        if hidden:
            self.button_icon_toggled.hide()

    def show(self):
        shown = super().show()
        if shown:
            if self.toggled:
                self.button_icon_toggled.show()
                self.button_icon.hide()
            else:
                self.button_icon_toggled.hide()
                self.button_icon.show()

    def destroy(self):
        super().destroy()
        self.button_icon_toggled.destroy()

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.toggled ^= True
            self.toggle()

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "button_icon_toggled"):
            self.button_icon_toggled.set_pos(pos.sub(self.button_icon_half))
        return super().set_pos(pos)
    
    def set_action_callback(self, callback: Callable):
        return super().set_action_callback(callback)
    
    def toggled_action_callback(self, callback: Callable):
        self.toggled_action = callback

    def toggle(self):
        if self.toggled:
            self.button_icon_toggled.show()
            self.button_icon.hide()
            self.set_tooltip_text("Hide polygon outline")
            if self.toggled_action: self.toggled_action()
        else:
            self.button_icon_toggled.hide()
            self.button_icon.show()
            self.set_tooltip_text("Show polygon outline")
            if self.action: self.action()

class OutlineSettingsMenuButton(CircularMenuButton):
    def __init__(self, mod_api: ModAPI, parent: Frame):
        super().__init__(mod_api, parent, "graphics/file_preview.png", "Outline Settings")

    def on_mouse_release(self, position: Vector2D):
        if self.action and self.contains_point(position):
            self.action()

class OffmapSettingsMenuButton(CircularMenuButton):
    def __init__(self, mod_api: ModAPI, parent: Frame):
        super().__init__(mod_api, parent, "graphics/keyboard_solid.png", "Hotkey Settings")

    def on_mouse_release(self, position: Vector2D):
        if self.action and self.contains_point(position):
            self.action()

class OutlineCycleModeMenuButton(CircularMenuButton):
    def __init__(self, parent: Frame, mod_api: ModAPI):
        super().__init__(mod_api, parent, "graphics/poly_outline.png", "Line mode")
        self.icon_fill = mod_api.create_interface_image(
            "graphics/poly_filled.png",
            scale=Vector2D(0.35, 0.35)
        )
        self.icon_lineonly = mod_api.create_interface_image(
            "graphics/poly_only_outline.png",
            scale=Vector2D(0.35, 0.35)
        )
        self.colorables.append(self.icon_fill)
        self.colorables.append(self.icon_lineonly)
        self.icon_fill.hide()
        self.icon_lineonly.hide()

        self.state = 1
        self.tooltips = ["Fill mode", "Line mode", "Line only mode"]
        self.callback: Callable[[int], None] | None = None

    def hide(self):
        hidden = super().hide()
        if hidden:
            self.icon_fill.hide()
            self.icon_lineonly.hide()

    def show(self):
        shown = super().show()
        if shown:
            self.button_icon.hide()
            self.icon_fill.hide()
            self.icon_lineonly.hide()
            
            if self.state == 0:
                self.icon_fill.show()
            elif self.state == 1:
                self.button_icon.show()
            else:
                self.icon_lineonly.show()
            self.set_tooltip_text(self.tooltips[self.state])

    def destroy(self):
        super().destroy()
        self.icon_fill.destroy()
        self.icon_lineonly.destroy()

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.state = (self.state + 1) % 3
            self.apply_mode()

    def apply_mode(self):
        self.button_icon.hide()
        self.icon_fill.hide()
        self.icon_lineonly.hide()
        if self.state == 0:
            self.icon_fill.show()
        elif self.state == 1:
            self.button_icon.show()
        else:
            self.icon_lineonly.show()

        self.set_tooltip_text(self.tooltips[self.state])
        if self.callback:
            self.callback(self.state)

    def set_pos(self, pos: Vector2D):
        offset = pos.sub(self.button_icon_half)
        if hasattr(self, "icon_fill"):
            self.icon_fill.set_pos(offset)
            self.icon_lineonly.set_pos(offset)
        return super().set_pos(pos)

    def set_callback(self, callback: Callable[[int], None]):
        self.callback = callback

class ToggleSceneryMenuButton(CircularMenuButton):
    def __init__(self, parent: Frame, mod_api: ModAPI):
        super().__init__(mod_api, parent, "graphics/fa-eye-solid.png", "Hide scenery")
        self.button_icon_toggled = mod_api.create_interface_image(
            "graphics/fa-eye-slash-solid.png", 
            scale=Vector2D(0.35, 0.35)
        )
        self.colorables.append(self.button_icon_toggled)
        self.button_icon_toggled.hide()
        self.toggled = False
        self.toggled_action = None

    def hide(self):
        hidden = super().hide()
        if hidden:
            self.button_icon_toggled.hide()

    def show(self):
        shown = super().show()
        if shown:
            if self.toggled:
                self.button_icon_toggled.show()
                self.button_icon.hide()
            else:
                self.button_icon_toggled.hide()
                self.button_icon.show()

    def destroy(self):
        super().destroy()
        self.button_icon_toggled.destroy()

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.toggled ^= True
            self.toggle()

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "button_icon_toggled"):
            self.button_icon_toggled.set_pos(pos.sub(self.button_icon_half))
        return super().set_pos(pos)
    
    def set_action_callback(self, callback: Callable):
        return super().set_action_callback(callback)
    
    def toggled_action_callback(self, callback: Callable):
        self.toggled_action = callback

    def toggle(self):
        if self.toggled:
            self.button_icon_toggled.show()
            self.button_icon.hide()
            self.set_tooltip_text("Hide scenery")
            if self.toggled_action: self.toggled_action()
        else:
            self.button_icon_toggled.hide()
            self.button_icon.show()
            self.set_tooltip_text("Show scenery")
            if self.action: self.action()
