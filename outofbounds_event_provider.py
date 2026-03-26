from soldat_extmod_api.mod_api import ModAPI, MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE, PAGE_READWRITE, Event

PATCH_ADDRESS = 0x005896A1
RANDOMIZE_START_FUNC_ADDR = 0x0058969A

CHECK_OOB_HOOK_CODE = f"""
push ecx
mov ecx, dword ptr ds:[pOwn_tsprite_address]
cmp ebx, ecx
pop ecx
jne flow_noevent
inc dword ptr ds:[oob_event_counter]
flow_noevent:
    call TSprite.Respawn

jmp 0x005896A6
""".strip()

class OutOfBoundsEventProvider:
    def __init__(self, mod_api: ModAPI, target_player_tsprite_address: int) -> None:
        self.api = mod_api
        self.own_tsprite_address = target_player_tsprite_address
        self.tsprite_ptr = self.api.soldat_bridge.allocate_memory(4, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.api.soldat_bridge.write(self.tsprite_ptr, self.own_tsprite_address.to_bytes(4, "little"))
        self.oob_event_counter = self.api.soldat_bridge.allocate_memory(4, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.__hook_address = 0
        self.hooked = False
        self.__random_start_original_code = self.api.soldat_bridge.read(RANDOMIZE_START_FUNC_ADDR, 5)
        self.api.subscribe_event(self.on_join, Event.DIRECTX_READY)

    def patch(self):
        if self.hooked:
            return
        self.api.assembler.add_to_symbol_table({
            "oob_event_counter": self.oob_event_counter,
            "pOwn_tsprite_address": self.tsprite_ptr
        })
        dummy_len = len(self.api.assembler.assemble(CHECK_OOB_HOOK_CODE, 0))
        self.__hook_address = self.api.soldat_bridge.allocate_memory(dummy_len, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
        self.api.soldat_bridge.write(
            self.__hook_address, 
            self.api.assembler.assemble(
                CHECK_OOB_HOOK_CODE,
                self.__hook_address
            )
        )
        self.api.soldat_bridge.write(
            PATCH_ADDRESS,
            self.api.assembler.assemble(
                f"jmp 0x{self.__hook_address:X}", 
                PATCH_ADDRESS
            )
        )
        self.hooked = True

    def is_oob(self):
        if not self.hooked:
            return False
        oob = int.from_bytes(self.api.soldat_bridge.read(self.oob_event_counter, 4), "little")
        if oob != 0:
            self.api.soldat_bridge.write(self.oob_event_counter,  b"\x00"*4)
            return True
        return False

    def disable_random_start(self):
        self.api.soldat_bridge.write(RANDOMIZE_START_FUNC_ADDR, b"\x90"*5)

    def enable_random_start(self):
        self.api.soldat_bridge.write(RANDOMIZE_START_FUNC_ADDR, self.__random_start_original_code)

    def on_join(self):
        own_player = self.api.get_player(self.api.get_own_id())
        self.api.soldat_bridge.write(self.tsprite_ptr, own_player.tsprite_object_addr.to_bytes(4, "little"))
