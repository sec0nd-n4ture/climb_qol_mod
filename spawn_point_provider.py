from struct import unpack
from enum import Enum
from pathlib import Path
from soldat_extmod_api.mod_api import Vector2D, ModAPI
from random import randint, choice

class SpawnType(Enum):
    General = 0
    Alpha = 1
    Bravo = 2
    Charlie = 3
    Delta = 4
    AlphaFlag = 5
    BravoFlag = 6
    Grenades = 7
    Medikits = 8
    Clusters = 9
    Vest = 10
    Flamer = 11
    Berserker = 12
    Predator = 13
    YellowFlag = 14
    RamboBow = 15
    StatGun = 16

class SpawnPoint:
    def __init__(self, active, x, y, spawn_type: SpawnType):
        self.active = active
        self.x = x
        self.y = y
        self.type = SpawnType._value2member_map_[spawn_type]

def get_current_spawnpoints(mod_api: ModAPI, team: int) -> list[Vector2D] | None:
    with open(mod_api.map_graphics.get_filename(), 'rb') as fd:
        data = fd.read()

        poly_count = unpack("I", data[88:92])[0]
        
        sector_count_offset = (poly_count * 121 + 4) + 92
        sector_count = unpack("I", data[sector_count_offset:sector_count_offset+4])[0]
        sectors_offset = sector_count_offset + 4
        n = (sector_count * 2 + 1) ** 2
        cursor = sectors_offset
        for _ in range(n):
            sector_poly_count = unpack("H", data[cursor:cursor+2])[0]
            cursor += 2
            cursor += sector_poly_count * 2
        prop_count = unpack("I", data[cursor:cursor+4])[0]
        cursor += 4
        cursor += prop_count * 44
        scenery_count = unpack("I", data[cursor:cursor+4])[0]
        cursor += 4
        cursor += scenery_count * 55
        collider_count = unpack("I", data[cursor:cursor+4])[0]
        cursor += 4
        spawn_points_offset = cursor + (16 * collider_count)
        cursor = spawn_points_offset
        spawn_points_count = unpack("I", data[cursor:cursor+4])[0]
        cursor += 4
        spawn_points: list[SpawnPoint] = []
        for i in range(spawn_points_count):
            spawn_points.append(SpawnPoint(*unpack("?iii", data[cursor:cursor+16])))
            cursor += 16

        if team not in (1, 2, -1):
            raise ValueError(f"Expected alpha or bravo spawnpoint, got {str(team)}")
        spawns = []
        for point in spawn_points:
            if point.active:
                if point.type.value == team:
                    spawns.append(Vector2D(point.x, point.y))
                if team == -1: # use any
                    spawns.append(Vector2D(point.x, point.y))
        return spawns

def internal_randomize_start(spawn_points: list[Vector2D]) -> Vector2D:
    start = Vector2D.zero()
    if spawn_points:
        rand_start = choice(spawn_points)
        start.x = rand_start.x - 4 + float(randint(0, 8))
        start.y = rand_start.y - 4 + float(randint(0, 4))


    return start
