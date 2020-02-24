import asyncio
import socket
import json
from hashlib import sha1
from kademlia.protocol import KademliaNode
from random import getrandbits


class DHTServer:
    def __init__(self, addr, id=None):
        self.id = id if id is not None else getrandbits(160)
        self.server : KademliaNode = None
        self.addr = addr
        self.loop = None

    async def run(self, bootstrap=None):
        self.loop = asyncio.get_running_loop()
        self.server = KademliaNode(self.id)
        _, _ = await self.loop.create_datagram_endpoint(lambda: self.server, local_addr=('0.0.0.0', self.addr[1]))
        if bootstrap is not None:
            await self.server.bootstrap(bootstrap)

    async def get_chunk(self, coord):
        key = int(sha1(str(coord).encode()).hexdigest(), 16)  # sha1 is 160 bits so useful for kademlia.
        value = None
        if key in self.server.chunks:
            value = self.server.chunks[key]
        else:
            value = await self.server.lookup(key, value=True, find_type=self.server.ext_find_chunk)
        print(f"find?{value}")
        if value is not None:
            addr = json.loads(value)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((addr["ip"],addr["port"]))
                s.send(json.dumps({"type": "ping"}).encode())
                if s.recv(4) == b'pong':
                    return value
            finally:
                print("finally")
                return None
        return value

    async def get_player(self, name):
        key = int(sha1(name.encode()).hexdigest(), 16)
        value = None
        if key in self.server.players:
            value = self.server.players[key]
        else:
            value = await self.server.lookup(key, value=True, find_type=self.server.ext_find_player)
        return json.loads(value) if value else None

    async def save_player(self, name, location):
        key = int(sha1(name.encode()).hexdigest(), 16)
        await self.server.insert(key, json.dumps({"pos":location}), store_type=self.server.ext_store_player)

    async def republish_chunk(self, coord, addr):
        key = int(sha1(str(coord).encode()).hexdigest(), 16)
        await self.server.insert(key, json.dumps({"ip": addr[0], "port": addr[1]}), store_type=self.server.ext_store_chunk)

    async def generate_chunk(self, coord):
        key = int(sha1(str(coord).encode()).hexdigest(), 16)
        nodes = await self.server.lookup(key)
        for i in range(len(nodes)):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = (nodes[i].addr[0], nodes[i].addr[1]+1)
            try:
                s.connect(addr)
                s.send(json.dumps({"type": "generate", "chunk": coord}).encode())
                if s.recv(2) == b'ok':
                    addr = json.dumps({"ip": addr[0], "port": addr[1]})
                    # incremented port because game port = kademlia port + 1 for simplicity's sake.
                    await self.server.insert(key, addr, store_type=self.server.ext_store_chunk)
                    return addr
            except ConnectionError:
                print("Node down, trying next or dying gracefully")
        return None
