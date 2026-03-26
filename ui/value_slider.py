from soldat_extmod_api.graphics_helper.gui_addon import \
    SliderBar, SliderKnob
from soldat_extmod_api.mod_api import ModAPI, Vector2D
from typing import Callable


class ValueSlider(SliderBar):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float,
            value_change_callback: Callable[[int], None],
            centered: bool = True
        ):
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "graphics/slider.png",
                scale=Vector2D(0.5, 0.5),
            ), 
            mod_api.create_interface_image(
                "graphics/slider.png",
                scale=Vector2D(0.5, 0.5)
            ), 
            centered
        )
        self.knob = SliderKnob(
            self, 
            0, 
            -2.5,
            mod_api.create_interface_image(
                "graphics/slider_knob.png",
                scale=Vector2D(0.5, 0.5)
            ), 
            0
        )
        self.hidden = False
        self.value_callback = value_change_callback

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.knob.image.hide()
            self.image.hide()
            self.slider_filled.hide()
            self.unsubscribe()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.knob.image.show()
            self.image.show()
            self.slider_filled.show()
            self.subscribe()

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.knob.image.destroy()
        self.slider_filled.destroy()


class BrightnessSlider(ValueSlider):
    def __init__(self, mod_api, parent, padding_x, padding_y, value_change_callback, centered = True):
        super().__init__(mod_api, parent, padding_x, padding_y, value_change_callback, centered)

    def on_click(self, position):
        super().on_click(position)
        if self.dragging:
            self.value_callback(self.get_brightness())

    def set_brightness(self, rgba_bytes: bytes) -> None:
        if len(rgba_bytes) < 3:
            raise ValueError("Incomplete color value")
        r = rgba_bytes[0]
        g = rgba_bytes[1]
        b = rgba_bytes[2]
        brightness_byte = max(r, g, b)

        self.knob.index = brightness_byte
        self.knob.update_percentage(self.knob.index)

    def get_brightness(self) -> int:
        return max(0, min(255, self.knob.index))

class TransparencySlider(ValueSlider):
    def __init__(self, mod_api, parent, padding_x, padding_y, value_change_callback, centered = True):
        super().__init__(mod_api, parent, padding_x, padding_y, value_change_callback, centered)

    def on_click(self, position):
        super().on_click(position)
        if self.dragging:
            self.value_callback(self.get_alpha())

    def set_alpha(self, rgba_bytes: bytes) -> None:
        if len(rgba_bytes) < 4:
            raise ValueError("Incomplete color value")
        alpha = rgba_bytes[3]
        self.knob.index = alpha
        self.knob.update_percentage(self.knob.index)

    def get_alpha(self) -> int:
        return max(0, min(255, self.knob.index))

