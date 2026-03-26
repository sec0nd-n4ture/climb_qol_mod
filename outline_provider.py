from soldat_extmod_api.mod_api import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE
from soldat_extmod_api.mod_api import ModAPI,Color
from poly_type import PolyType
from pms_parser import Map
import logging

class OutlineProvider:
    def __init__(self, config: dict[str, str], mod_api: ModAPI):
        self.config = config
        self.api = mod_api
        self.visible = False
        self.outline_mode = "line"

    def update_wireframe(self):
        map_vertex_data = bytearray(self.api.get_current_map_vertexdata())
        vert_size = self.api.get_current_map_vertexdata_size()

        back_start = self.api.map_graphics.get_polys_back()
        back_count = self.api.map_graphics.get_polys_back_count()
        front_start = self.api.map_graphics.get_polys_front()
        front_count = self.api.map_graphics.get_polys_front_count()

        cur_map = Map.from_file(self.api.map_graphics.get_filename())
        all_polygons = cur_map.polygons

        BACKPOLY_VALUES = [PolyType.BACKGROUND.value,
                           PolyType.BACKGROUND_TRANSITION.value]


        back_polys = [p for p in all_polygons if p.type in BACKPOLY_VALUES]
        front_polys = [p for p in all_polygons if p.type not in BACKPOLY_VALUES]

        if len(back_polys) * 3 != back_count or len(front_polys) * 3 != front_count:
            logging.warning("Polygon count mismatch, vertex buffer may be out of sync")

        stride = 20
        color_offset = 16

        for idx, poly in enumerate(back_polys):
            vertex_base = (back_start + idx * 3) * stride
            for v in range(3):
                pos = vertex_base + v * stride + color_offset
                type_name = PolyType._value2member_map_[poly.type].name
                map_vertex_data[pos:pos+4] = bytes.fromhex(self.config[type_name])

        for idx, poly in enumerate(front_polys):
            vertex_base = (front_start + idx * 3) * stride
            for v in range(3):
                pos = vertex_base + v * stride + color_offset
                type_name = PolyType._value2member_map_[poly.type].name
                map_vertex_data[pos:pos+4] = bytes.fromhex(self.config[type_name])


        wireframe_vbo_addr = self.api.soldat_bridge.allocate_memory(
            vert_size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
        )
        self.api.soldat_bridge.write(wireframe_vbo_addr, bytes(map_vertex_data))
        wireframe_vbo = self.api.create_vertex_buffer(vert_size // stride, True, wireframe_vbo_addr)
        self.api.set_polygon_wireframe_vbo(wireframe_vbo)
        self.api.soldat_bridge.free_memory(wireframe_vbo_addr)

    def toggle(self):
        self.visible ^= True
        if self.visible:
            self.api.enable_polygon_wireframe()
        else:
            self.api.disable_polygon_wireframe()

    def hide(self):
        self.visible = False
        self.api.disable_polygon_wireframe()
        self.api.enable_polygon_layer()
        self.api.enable_backpoly_layer()

    def show(self):
        self.visible = True
        self.api.enable_polygon_wireframe()
        if self.outline_mode in ["fill", "outline_only"]:
            self.api.disable_polygon_layer()
            self.api.disable_backpoly_layer()
