from soldat_extmod_api.mod_api import ModAPI, Color, FontStyle, Vector2D, ImageNode
from soldat_extmod_api.graphics_helper.gui_addon import Button
from typing import Callable


class ActionButton(Button):
    def __init__(self, mod_api: ModAPI, parent, padding_x: float, padding_y: float, image: ImageNode):
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            image,
            False
        )
        self.action : None | Callable = None
        self.hidden = False

    def on_cursor_enter(self):
        self.image.set_color(Color("70%", "70%", "70%", "100%"))

    def on_cursor_exit(self):
        self.image.set_color(Color.from_hex("ffffffff"))

    def on_mouse_release(self, position: Vector2D):
        if self.action and self.contains_point(position):
            if hasattr(self, "action_args"):
                self.action(self.action_args)
            else:
                self.action()

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


class CloseButton(ActionButton):
    def __init__(
            self, mod_api: ModAPI, parent, 
            padding_x: float, padding_y: float,
            action_callback: Callable[[], None]
        ):
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y,
            mod_api.create_interface_image(
                "graphics/button_close.png",
                scale=Vector2D(0.35, 0.35)
            ), 
        )
        self.action = action_callback

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)

    def hide(self):
        super().hide()

    def show(self):
        super().show()

class CycleButton(ActionButton):
    def __init__(
            self, mod_api: ModAPI, parent, 
            padding_x: float, padding_y: float, direction: int,
            action_callback: Callable[[int], None]
        ):
        image_dir = "graphics/fa-arrow-right-solid.png" if direction else "graphics/fa-arrow-left-solid.png"
        self.direction = direction
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y,
            mod_api.create_interface_image(
                image_dir,
                scale=Vector2D(0.7, 0.7)
            ), 
        )
        self.action = action_callback
        self.action_args = self.direction


    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)

    def hide(self):
        super().hide()

    def show(self):
        super().show()

class SaveButton(ActionButton):
    def __init__(self, mod_api: ModAPI, parent, padding_x: float, padding_y: float):
        self.button_desc = mod_api.create_interface_text(
            "Save",
            Vector2D.zero(),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(1, 2),
            FontStyle.FONT_WEAPONS_MENU,
            0.5
        )
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y,
            mod_api.create_interface_image(
                "graphics/file_solid.png",
                scale=Vector2D(0.47, 0.47)
            ), 
        )

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)
        self.button_desc.set_pos(pos + Vector2D(-2, 20))

    def hide(self):
        super().hide()
        self.button_desc.hide()

    def show(self):
        super().show()
        self.button_desc.show()
