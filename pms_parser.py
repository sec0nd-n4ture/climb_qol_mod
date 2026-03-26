from soldat_extmod_api.graphics_helper.vector_utils import Vector3D
from custom_buffer_reader import BufferReader, BufferWriter
from soldat_extmod_api.graphics_helper.color import Color


class ColorBGRA(Color):
    def __init__(self, blue: int | str = 0, green: int | str = 0, red: int | str = 0, alpha: int | str = 0):
        super().__init__(red, green, blue, alpha)

    def to_bytes(self):
        return self.blue.to_bytes(1, "little") + \
               self.green.to_bytes(1, "little") + \
               self.red.to_bytes(1, "little") + \
               self.alpha.to_bytes(1, "little")
    
    @classmethod
    def from_bytes(cls, colorhex: bytes):
        cls = ColorBGRA(int().from_bytes(colorhex[0:1], "little"),
                        int().from_bytes(colorhex[1:2], "little"),
                        int().from_bytes(colorhex[2:3], "little"),
                        int().from_bytes(colorhex[3:4], "little"))
        return cls
    
    def to_int_tuple(self):
        return self.red, self.green, self.blue

class Vertex:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.rhw = 0
        self.color = None
        self.u = 0
        self.v = 0
    
class Polygon:
    def __init__(self) -> None:
        self.vertices = [Vertex(), Vertex(), Vertex()]
        self.normals = [Vector3D.zero(), Vector3D.zero(), Vector3D.zero()]
        self.type = 0

    def to_float_tuple(self):
        return [(v.x, v.y) for v in self.vertices]



class Map:
    def __init__(self):
        self.version = 0
        self.name = ""
        self.texture = ""
        self.background_color_top: ColorBGRA = None
        self.background_color_bottom: ColorBGRA = None
        self.jet_amount = 0
        self.grenades = 0
        self.medikits = 0
        self.weather = 0
        self.steps = 0
        self.randId = 0
        self.polygons: list[Polygon] = []
        self.sectorsDivision = 0
        self.numSectors = 25
        self.sectors = []
        self.props = []
        self.scenery = []
        self.colliders = []
        self.spawns = []
        self.waypoints = []
        self.data_rest = b""


    @classmethod
    def from_file(cls, dir: str):
        cls = Map()
        with open(dir, "rb") as fd:
            data = fd.read()

        reader = BufferReader(data)
        cls.version = reader.read_and_unpack("i")
        cls.name = reader.read_and_unpack("39s")
        cls.texture = reader.read_and_unpack("25s")
        cls.background_color_top = ColorBGRA.from_bytes(reader.read(4))
        cls.background_color_bottom = ColorBGRA.from_bytes(reader.read(4))
        cls.jet_amount = reader.read_and_unpack("i")
        cls.grenades = reader.read_and_unpack("B")
        cls.medikits = reader.read_and_unpack("B")
        cls.weather = reader.read_and_unpack("B")
        cls.steps = reader.read_and_unpack("B")
        cls.randId = reader.read_and_unpack("i")
    
        for i in range(reader.read_and_unpack("I")):
            polygon = Polygon()

            for j in range(3):
                polygon.vertices[j].x = reader.read_and_unpack("f")
                polygon.vertices[j].y = reader.read_and_unpack("f")
                polygon.vertices[j].z = reader.read_and_unpack("f")
                polygon.vertices[j].rhw = reader.read_and_unpack("f")
                polygon.vertices[j].color = ColorBGRA.from_bytes(reader.read(4))
                polygon.vertices[j].u = reader.read_and_unpack("f")
                polygon.vertices[j].v = reader.read_and_unpack("f")

            for j in range(3):
                polygon.normals[j].x = reader.read_and_unpack("f")
                polygon.normals[j].y = reader.read_and_unpack("f")
                polygon.normals[j].z = reader.read_and_unpack("f")

            polygon.type = reader.read_and_unpack("B")
            cls.polygons.append(polygon)
        cls.sectorsDivision = reader.read_and_unpack("I")
        cls.numSectors = reader.read_and_unpack("I")
        cls.data_rest = reader.read()

        reader.close()
        return cls

    def save(self, fname: str):
        writer = BufferWriter()
        writer.pack_and_write("i", self.version)
        writer.pack_and_write("39s", self.name)
        writer.pack_and_write("25s", self.texture)
        writer.write(self.background_color_top.to_bytes())
        writer.write(self.background_color_bottom.to_bytes())
        writer.pack_and_write("i", self.jet_amount)
        writer.pack_and_write("B", self.grenades)
        writer.pack_and_write("B", self.medikits)
        writer.pack_and_write("B", self.weather)
        writer.pack_and_write("B", self.steps)
        writer.pack_and_write("i", self.randId)