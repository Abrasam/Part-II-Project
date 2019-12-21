import random
import json

from game.const import PacketType

CHUNK_SIZE = 32


class Chunk:
    def __init__(self, x, y):
        self.data = [[[0 for i in range(0, CHUNK_SIZE)] for i in range(0, CHUNK_SIZE)] for k in range(0, CHUNK_SIZE)]
        self.location = (x, y)

    def generate(self):
        for i in range(0, CHUNK_SIZE):
            for j in range(0, CHUNK_SIZE):
                for k in range(0, CHUNK_SIZE):
                    self.data[i][j][k] = 1

    def encode(self):
        def pack(l):
            out = []
            for i in l:
                out += i
            return out
        compress = pack(list(map(lambda x: pack(list(map(lambda y: pack(y),x))), self.data)))
        return json.dumps({"type" : PacketType.CHUNK_DATA.value, "args" : list(self.location) + compress).encode()


class Player:
    def __init__(self, id, name, x, y):
        self.id = id
        self.name = name
        self.location = (x, y)