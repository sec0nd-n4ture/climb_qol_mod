from soldat_extmod_api.graphics_helper.gui_addon import Container
from ui.value_slider import BrightnessSlider, TransparencySlider
from soldat_extmod_api.mod_api import ModAPI, Vector2D, Color
from typing import Callable

class BrightnessSliderContainer(Container):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float,
            brightness_callback: Callable[[int], None]
        ):
        super().__init__(
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "graphics/slider_back.png",
                scale=Vector2D(0.5, 0.5),
                color=Color.from_hex("161821ff")
            ), 
            True
        )
        self.hidden = False
        self.mod_api = mod_api
        self.brightness_slider = BrightnessSlider(self.mod_api, self, 0, 0, brightness_callback, True)
        self.brightness_slider.image.set_color(Color.from_hex("494e69ff"))
        self.brightness_slider.slider_filled.set_color(Color.from_hex("191b24ff"))
        self.brightness_slider.knob.map_percentage(255)

    def hide(self):
        self.image.hide()
        self.brightness_slider.hide()

    def show(self):
        self.image.show()
        self.brightness_slider.show()

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.brightness_slider.destroy()

class TransparencySliderContainer(Container):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float,
            transparency_callback: Callable[[int], None]
        ):
        super().__init__(
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "graphics/slider_back.png",
                scale=Vector2D(0.5, 0.5),
                color=Color.from_hex("161821ff")
            ), 
            True
        )
        self.hidden = False
        self.mod_api = mod_api
        self.transparency_slider = TransparencySlider(self.mod_api, self, 0, 0, transparency_callback, True)
        self.transparency_slider.image.set_color(Color.from_hex("494e69ff"))
        self.transparency_slider.slider_filled.set_color(Color.from_hex("191b24ff"))
        self.transparency_slider.knob.map_percentage(255)

    def hide(self):
        self.image.hide()
        self.transparency_slider.hide()

    def show(self):
        self.image.show()
        self.transparency_slider.show()

    def destroy(self):
        self.hide()
        self.image.destroy()
        self.transparency_slider.destroy()
