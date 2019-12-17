from enum import Enum


class Commands(Enum):
    FIND_CHUNK = 0
    PLAYER_REGISTER = 1
    PLAYER_DEREGISTER = 2
    PLAYER_MOVE = 2
    FIND_PLAYER = 4


class ClientType(Enum):
    PLAYER = 1
    SERVER = 2


TICK_LENGTH = 1/20
