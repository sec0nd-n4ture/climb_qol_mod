from soldat_extmod_api.mod_api import ModAPI


class TransparencyControlsPatch:
    '''
    Allows mod to prevent Soldat from controlling player transparency
    '''
    def __init__(self, mod_api: ModAPI) -> None:
        self.mod_api = mod_api
        self.patch_applied = False
        self.__orig_code_0x00583C52 = self.mod_api.soldat_bridge.read(0x00583C52, 3)
        self.__orig_code_0x00583C57 = self.mod_api.soldat_bridge.read(0x00583C57, 4)
        self.__orig_code_0x00586A54 = self.mod_api.soldat_bridge.read(0x00586A54, 4)
        self.__orig_code_0x00545A0A = self.mod_api.soldat_bridge.read(0x00545A0A, 8)

    def apply_patch(self) -> None:
        self.mod_api.soldat_bridge.write(0x00583C52, b"\x90"*3)
        self.mod_api.soldat_bridge.write(0x00583C57, b"\x90"*4)
        self.mod_api.soldat_bridge.write(0x00586A54, b"\x90"*4)
        self.mod_api.soldat_bridge.write(0x00545A0A, b"\x90"*8)
        self.patch_applied = True

    def remove_patch(self) -> None:
        self.mod_api.soldat_bridge.write(0x00583C52, self.__orig_code_0x00583C52)
        self.mod_api.soldat_bridge.write(0x00583C57, self.__orig_code_0x00583C57)
        self.mod_api.soldat_bridge.write(0x00586A54, self.__orig_code_0x00586A54)
        self.mod_api.soldat_bridge.write(0x00545A0A, self.__orig_code_0x00545A0A)
        self.patch_applied = False

