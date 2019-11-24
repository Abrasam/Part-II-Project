import asyncio
import hashlib
from kademlia.server import KademliaServer
from kademlia.node import Node
from random import getrandbits

class Kademlia:
    def __init__(self, addr, id=None):
        self.id = id if id is not None else getrandbits(160)
        self.server = None
        self.addr = addr

    async def run(self, bootstrap=None):
        loop = asyncio.get_running_loop()
        print(self.addr)
        self.server = KademliaServer(self.id)
        await loop.create_datagram_endpoint(lambda: self.server, local_addr=self.addr)
        if bootstrap is not None:
            await self.server.bootstrap(bootstrap)

    async def get(self, key):
        key = int(hashlib.sha1(key).hexdigest(), 16)  # sha1 is 160 bits so useful for kademlia.
        if key in self.server.storage:
            return self.server.storage[key]
        print("We didn't have it so we'll ask someone else")
        value = await self.server.lookup(key, value=True)
        return value

    async def set(self, key, value):
        key = int(hashlib.sha1(key).hexdigest(), 16)
        nodes = await self.server.lookup(key)
        if self.id ^ key <= max(map(lambda n: n.id ^ key, nodes)):
            self.server.storage[key] = value
        asyncio.ensure_future(asyncio.gather(*[self.server.ext_store(n, key, value) for n in nodes]))
