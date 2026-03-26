from enum import Enum


class PolyType(Enum):
    NORMAL                = 0
    ONLY_BULLETS          = 1
    ONLY_PLAYER           = 2
    DOESNT                = 3
    ICE                   = 4
    DEADLY                = 5
    BLOODY_DEADLY         = 6
    HURTS                 = 7
    REGENERATES           = 8
    LAVA                  = 9
    RED_BULLETS           = 10
    RED_PLAYER            = 11
    BLUE_BULLETS          = 12
    BLUE_PLAYER           = 13
    YELLOW_BULLETS        = 14
    YELLOW_PLAYER         = 15
    GREEN_BULLETS         = 16
    GREEN_PLAYER          = 17
    BOUNCY                = 18
    EXPLODES              = 19
    HURTS_FLAGGERS        = 20
    ONLY_FLAGGERS         = 21
    NOT_FLAGGERS          = 22
    NON_FLAGGER_COLLIDES  = 23
    BACKGROUND            = 24
    BACKGROUND_TRANSITION = 25
