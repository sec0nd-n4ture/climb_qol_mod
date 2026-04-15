from soldat_extmod_api.mod_api import ModAPI

PATCH_BYTES = b"\xE9\x53\x03\x00\x00\x90"
PATCH_ADDRESS = 0x00544976
MOUSE_CLAMP_ADDRESS = 0x00545273
MOUSE_CLAMP_PATCH = b"\xEB\x7C\x90\x90\x90" # jmp 0x005452F1; nop; nop; nop

class CameraControls:
    def __init__(self, mod_api: ModAPI) -> None:
        self.api = mod_api
        self.__original_code = self.api.soldat_bridge.read(PATCH_ADDRESS, len(PATCH_BYTES))
        self.__original_code_clamp = self.api.soldat_bridge.read(
            MOUSE_CLAMP_ADDRESS, len(MOUSE_CLAMP_PATCH)
        )

    def take_controls(self):
        self.api.soldat_bridge.write(PATCH_ADDRESS, PATCH_BYTES)

    def restore_controls(self):
        self.api.soldat_bridge.write(PATCH_ADDRESS, self.__original_code)

    def disable_mouse_clamping(self):
        self.api.soldat_bridge.write(MOUSE_CLAMP_ADDRESS, MOUSE_CLAMP_PATCH)

    def enable_mouse_clamping(self):
        self.api.soldat_bridge.write(MOUSE_CLAMP_ADDRESS, self.__original_code_clamp)
