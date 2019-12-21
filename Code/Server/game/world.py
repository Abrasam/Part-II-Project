import random
import json

CHUNK_WIDTH = 64
# CHUNK_HEIGHT = 1


class Chunk:
    def __init__(self, x, y):
        self.data = [[0 for i in range(0, CHUNK_WIDTH)] for i in range(0, CHUNK_WIDTH)]
        self.location = (x, y)

    def generate(self):
        for i in range(0, CHUNK_WIDTH):
            for j in range(0, CHUNK_WIDTH):
                self.data[i][j] = random.random()

    def encode(self):
        return json.dumps({"data": self.data, "loc": self.location}).encode()


class Player:
    def __init__(self, id, name, x, y):
        self.id = id
        self.name = name
        self.location = (x, y)