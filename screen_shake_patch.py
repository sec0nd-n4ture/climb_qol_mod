from soldat_extmod_api.mod_api import ModAPI, Event

class ScreenShakePatch:
    def __init__(self, mod_api: ModAPI) -> None:
        self.mod_api = mod_api
        self.mod_api.subscribe_event(self.on_directx_ready, Event.DIRECTX_READY)
        self.patch_applied = False

    def on_directx_ready(self) -> None:
        if not self.patch_applied:
            self.apply_patch()

    def apply_patch(self) -> None:
        self.mod_api.soldat_bridge.write(0x0058F398, b"\xEB\x6B")
        self.mod_api.soldat_bridge.write(0x0058C0E3, b"\xE9\x38\x01\x00\x00\x90")
        self.mod_api.soldat_bridge.write(0x00593A93, b"\xE9\xE4\x00\x00\x00\x90")

    def remove_patch(self) -> None:
        self.mod_api.soldat_bridge.write(0x0058F398, b"\x75\x6B")
        self.mod_api.soldat_bridge.write(0x0058C0E3, b"\x0F\x86\x37\x01\x00\x00")
        self.mod_api.soldat_bridge.write(0x00593A93, b"\x0F\x86\xE3\x00\x00\x00")

