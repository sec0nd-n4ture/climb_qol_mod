from soldat_extmod_api.mod_api import (
    ModAPI, Event, ImageNode,
    Vector2D, Vector3D,
    Color
)
import math

ARROW_INSET_FACTOR = 0.1

class PlayerPositionIndicator:
    def __init__(self, mod_api:  ModAPI):
        self.api = mod_api
        self.player = self.__get_own_player()
        self.api.subscribe_event(self.on_join, Event.DIRECTX_READY)
        self.api.subscribe_event(self.on_leave, Event.DIRECTX_NOT_READY)
        self.enabled = False
        self.visible = False
        self.arrow: ImageNode | None = None
        game_width_half_addr = self.api.soldat_bridge.read(
            self.api.addresses["game_width_half"], 4
        )
        self.game_scale_half = Vector2D.from_bytes(
            self.api.soldat_bridge.read(int.from_bytes(game_width_half_addr,"little"), 8)
        )
        self.pivot = Vector2D.zero()

    def on_join(self):
        self.player = self.__get_own_player()
        self.arrow = self.api.create_world_image(
            "graphics/indicator_arrow.png",
            color=Color("100%", "100%", "100%", "40%")
        )
        self.pivot.x = self.arrow.get_dimensions.x / 2
        self.pivot.y = self.arrow.get_dimensions.y / 2
        self.arrow.hide()

    def tick(self):
        if self.enabled:
            player_pos = self.player.get_position()
            camera_center = Vector2D.from_bytes(
                self.api.soldat_bridge.read(
                    self.api.addresses["camera_world_pos_x"],
                    8
                )
            )
            arrow_pos = self.__calculate_arrow_position(player_pos, camera_center)
            if arrow_pos is not None:
                position_delta = camera_center - player_pos
                self.arrow.set_pos(arrow_pos + self.game_scale_half)
                self.arrow.set_rotation(
                    Vector3D(*self.pivot.to_tuple(), math.atan2(*position_delta.to_tuple()))
                )
                if not self.visible:
                    self.show()
            else:
                self.hide()

    def on_leave(self):
        self.arrow.destroy()
        self.visible = False
        self.enabled = False

    def show(self):
        self.arrow.show()
        self.visible = True

    def hide(self):
        self.arrow.hide()
        self.visible = False

    def __get_own_player(self):
        return self.api.get_player(self.api.get_own_id())

    def __calculate_arrow_position(self, player_pos: Vector2D, camera_center: Vector2D):
        dx = player_pos.x - camera_center.x
        dy = player_pos.y - camera_center.y 
        
        half_w = self.game_scale_half.x
        half_h = self.game_scale_half.y
        
        if abs(dx) <= half_w and abs(dy) <= half_h:
            return None

        tx = half_w / abs(dx) if dx != 0 else float('inf')
        ty = half_h / abs(dy) if dy != 0 else float('inf')
        t = min(tx, ty)

        offset_t = min(
            (half_w * ARROW_INSET_FACTOR) / abs(dx) if dx != 0 else float('inf'),
            (half_h * ARROW_INSET_FACTOR) / abs(dy) if dy != 0 else float('inf')
        )
        t = max(0.0, t - offset_t)

        return Vector2D(camera_center.x + dx * t, camera_center.y + dy * t)

