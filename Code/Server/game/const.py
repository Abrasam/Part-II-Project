from enum import Enum


class PacketType(Enum):
    FIND_CHUNK = 0
    PLAYER_REGISTER = 1
    PLAYER_DEREGISTER = 2
    PLAYER_MOVE = 3
    FIND_PLAYER = 4
    CHUNK_DATA = 5
    TIME = 6
    BLOCK_CHANGE = 7


class ClientType(Enum):
    PLAYER = 1
    SERVER = 2


TICK_LENGTH = 1/20

CHUNK_SIZE = 32
