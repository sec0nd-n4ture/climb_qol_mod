from soldat_extmod_api.mod_api import ModAPI

PATCH_BYTES = b"\xE9\x53\x03\x00\x00\x90"
PATCH_ADDRESS = 0x00544976

class CameraControls:
    def __init__(self, mod_api: ModAPI) -> None:
        self.api = mod_api
        self.__original_code = self.api.soldat_bridge.read(PATCH_ADDRESS, len(PATCH_BYTES))

    def take_controls(self):
        self.api.soldat_bridge.write(PATCH_ADDRESS, PATCH_BYTES)

    def restore_controls(self):
        self.api.soldat_bridge.write(PATCH_ADDRESS, self.__original_code)

