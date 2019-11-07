import json
from random import getrandbits


def xor_distance(id1, id2):
    return id1 ^ id2


def rpc(func):
    def rpc_func(self, *args):
         msg = json.dumps({"id" : getrandbits(32), "rpc" : func.__name__,  "arg" : args})
    return rpc_func


class Node:
    def __init__(self, id, addr):
        self.id = id
        self.address = addr

    async def ping(self, source):
        pass

    async def find_node(self, id, source):
        pass

    async def find_value(self, id, source):
        pass

    async def store(self, key, value, source):
        pass



