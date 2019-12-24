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
        _, _ = await self.loop.create_datagram_endpoint(lambda: self.server, local_addr=self.addr)
        if bootstrap is not None:
            await self.server.bootstrap(bootstrap)

    async def get_chunk(self, coord):
        print(coord)
        key = int(sha1(str(coord).encode()).hexdigest(), 16)  # sha1 is 160 bits so useful for kademlia.
        if key in self.server.storage:
            return self.server.storage[key]
        value = await self.server.lookup(key, value=True)
        return value

    async def generate_chunk(self, coord):
        print(coord)
        key = int(sha1(str(coord).encode()).hexdigest(), 16)
        nodes = await self.server.lookup(key)
        print(nodes)
        if len(nodes) > 0:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = (nodes[0].addr[0], nodes[0].addr[1]+1)
            s.connect(addr)
            s.send(json.dumps({"type": "generate", "chunk": coord}).encode())
            if s.recv(2) == b'ok':
                addr = json.dumps({"ip": addr[0], "port": addr[1]})
                # incremented port because game port = kademlia port + 1 for simplicity's sake.
                await self.server.insert(key, addr)
                return addr
        return None
