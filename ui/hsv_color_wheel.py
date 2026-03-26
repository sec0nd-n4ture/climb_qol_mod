from soldat_extmod_api.graphics_helper.gui_addon import Container, Interactive
from soldat_extmod_api.mod_api import ModAPI, Vector2D
from ui.color_utils import hsv_to_rgb, rgb_to_hsv
from typing import Callable
import math

class HSVColorWheel(Container, Interactive):
    def __init__(
            self, parent, 
            padding_x, padding_y, 
            mod_api: ModAPI, 
            color_change_callback: Callable[[bytes], None]
        ):
        super().__init__(
            parent, 
            padding_x, padding_y, 
            mod_api.create_interface_image("graphics/color_circle.png", scale=Vector2D(0.5, 0.5)), 
            False
        )
        Interactive.__init__(self, mod_api)
        self.color_change_action: Callable[[bytes], None] = color_change_callback
        self.current_color = b"\xff\xff\xff\xff"
        self.hue = 0.0
        self.sat = 0.0
        self.value = 1.0
        self.alpha = 255
        self.hidden = False

        self.hide()

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.image.hide()
            self.unsubscribe()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.image.show()
            self.subscribe()

    def destroy(self):
        self.hide()
        self.image.destroy()

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)

    def on_mouse_release(self, position):
        if self.contains_point(position):
            hsv = self.position_to_hsv(position)
            if hsv is not None:
                self.hue, self.sat, _ = hsv
                self._update_color()

    def set_value(self, new_value: float):
        self.value = max(0.0, min(1.0, new_value))
        self._update_color()

    def set_alpha(self, new_alpha: int):
        self.alpha = max(0, min(255, new_alpha))
        self._update_color()

    def set_from_rgba(self, rgba_bytes: bytes):
        if len(rgba_bytes) < 4:
            raise ValueError("Incomplete color value")
        r, g, b, a = rgba_bytes[0], rgba_bytes[1], rgba_bytes[2], rgba_bytes[3]
        h, s, v = rgb_to_hsv(r, g, b)
        self.hue = h
        self.sat = s
        self.value = v
        self.alpha = a
        self._update_color()

    def _update_color(self):
        rgb_bytes = hsv_to_rgb((self.hue, self.sat, self.value))
        self.current_color = bytes([rgb_bytes[0], rgb_bytes[1], rgb_bytes[2], self.alpha])
        self.color_change_action(self.current_color)

    def position_to_hsv(self, position: Vector2D):
        local_x = position.x - self.position.x
        local_y = position.y - self.position.y

        w = self.dimensions.x * self.scale.x
        h = self.dimensions.y * self.scale.y

        if not (0 <= local_x <= w and 0 <= local_y <= h):
            return None

        cx = w / 2
        cy = h / 2
        dx = local_x - cx
        dy = local_y - cy
        dist = math.sqrt(dx*dx + dy*dy)

        radius = min(w, h) / 2
        if dist > radius:
            return None

        saturation = dist / radius

        angle_rad = math.atan2(-dy, -dx)
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0:
            angle_deg += 360


        hue = (angle_deg - 90) % 360

        return (hue, saturation, 1.0)

