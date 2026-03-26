from io import BytesIO
import struct


class BufferReader(BytesIO):
    def __init__(self, initial_bytes):
        super().__init__(initial_bytes)

    def read_and_unpack(self, struct_format: str):
        size = struct.calcsize(struct_format)
        data = self.read(size)
        unpacked = struct.unpack(struct_format, data)
        if len(unpacked) == 1: unpacked = unpacked[0]
        return unpacked
    
class BufferWriter(BytesIO):
    def __init__(self, initial_bytes):
        super().__init__(initial_bytes)
    
    def pack_and_write(self, struct_format: str, value):
        packed = struct.pack(struct_format, value)
        self.write(packed)