from soldat_extmod_api.mod_api import ModAPI, Event, Vector2D
from outofbounds_event_provider import OutOfBoundsEventProvider
from nonspec_camera_controls import CameraControls
import spawn_point_provider
from pms_parser import Map


class OffmapHotkey:
    def __init__(
            self, 
            api: ModAPI, 
            camera_controls: CameraControls, 
            oob_provider: OutOfBoundsEventProvider
        ):
        self.api = api
        self.api.subscribe_event(self.on_map_change, Event.MAP_CHANGE)
        self.current_map_spawn_points_alpha: list[Vector2D] | None = None
        self.current_map_spawn_points_bravo: list[Vector2D] | None = None
        self.current_map_spawn_points_any: list[Vector2D] | None = None
        self.map_bound = 0
        self.random_spawn = Vector2D.zero()
        self.use_camera_pinning = False
        self.on_limbo = False
        self.own_player = self.api.get_player(self.api.get_own_id())
        self.current_team = self.own_player.team
        self.camera_controls = camera_controls
        self.oob_provider = oob_provider

    def on_map_change(self, _: str) -> None:
        current_map = Map.from_file(self.api.map_graphics.get_filename())
        self.map_bound = current_map.numSectors * current_map.sectorsDivision - 50
        self.current_map_spawn_points_alpha = spawn_point_provider.get_current_spawnpoints(self.api, 1)
        self.current_map_spawn_points_bravo = spawn_point_provider.get_current_spawnpoints(self.api, 2)
        self.current_map_spawn_points_any = spawn_point_provider.get_current_spawnpoints(self.api, -1)

    def on_offmap_hotkey_pressed(self):
        if self.current_team in (1, 2) and not self.own_player.get_is_dead():
            self.go_offmap()

    def go_offmap(self):
        if not self.current_map_spawn_points_alpha or not self.current_map_spawn_points_bravo:
            self.random_spawn = spawn_point_provider.internal_randomize_start(self.current_map_spawn_points_any)
        else:
            self.random_spawn = spawn_point_provider.internal_randomize_start(
                self.current_map_spawn_points_alpha if self.current_team == 1 else self.current_map_spawn_points_bravo
            )
        self.on_limbo = True
        self.oob_provider.disable_random_start()
        if self.use_camera_pinning:
            self.camera_controls.take_controls()
            self.pin_camera()
        self.own_player.set_position(
            Vector2D(
                self.map_bound - 5, 
                self.map_bound - 5
        ).to_bytes())
        self.own_player.set_velocity(Vector2D.zero())

    def pin_camera(self):
        if self.use_camera_pinning:
            self.api.set_camera_position(self.random_spawn)

    def tick(self):
        self.current_team = self.own_player.team
        if self.on_limbo and self.oob_provider.is_oob():
            self.on_respawn()
            self.on_limbo = False

    def on_respawn(self):
        if self.current_team in (1, 2):
            self.own_player.set_position(self.random_spawn)
            if self.use_camera_pinning:
                self.camera_controls.restore_controls()
            self.oob_provider.enable_random_start()
