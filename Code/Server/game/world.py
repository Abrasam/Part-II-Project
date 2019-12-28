import random
import json

from noise import snoise2,snoise3
from game.const import PacketType

CHUNK_SIZE = 32


class Chunk:
    def __init__(self, x, y):
        self.data = [[[0 for _ in range(0, CHUNK_SIZE)] for _ in range(0, CHUNK_SIZE)] for _ in range(0, CHUNK_SIZE)]
        self.location = (x, y)
        self.generate()

    def generate(self):
        for i in range(0, CHUNK_SIZE):
            for j in range(0, CHUNK_SIZE):
                for k in range(0, CHUNK_SIZE):
                    x = self.location[0]*CHUNK_SIZE+i
                    y = j
                    z = self.location[1]*CHUNK_SIZE+k
                    height = int(0.5*(1+snoise2(x/100, z/100, octaves=3, lacunarity=2, persistence=0.5))*32)
                    if height > j:
                        if height - 4 > j:
                            self.data[i][j][k] = 1
                        else:
                            self.data[i][j][k] = 3
                    elif height == j:
                        self.data[i][j][k] = 2

    def encode(self):
        def pack(l):
            out = []
            for i in l:
                out += i
            return out
        compress = pack(list(map(lambda x: pack(x), self.data)))
        return {"type": PacketType.CHUNK_DATA.value, "args": list(self.location) + compress}


class Player:
    def __init__(self, id, name, x, y):
        self.id = id
        self.name = name
        self.location = (x, y)