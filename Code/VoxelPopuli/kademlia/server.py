import asyncio
import hashlib
from kademlia.protocol import KademliaNode
from random import getrandbits


class DHTServer:
    def __init__(self, addr, id=None):
        self.id = id if id is not None else getrandbits(160)
        self.server = None
        self.addr = addr

    async def run(self, bootstrap=None):
        loop = asyncio.get_running_loop()
        print(self.addr)
        self.server = KademliaNode(self.id)
        transport, protocol = await loop.create_datagram_endpoint(lambda: self.server, local_addr=self.addr)
        print(transport)
        if bootstrap is not None:
            await self.server.bootstrap(bootstrap)

    async def get(self, key):
        key = int(hashlib.sha1(key).hexdigest(), 16)  # sha1 is 160 bits so useful for kademlia.
        if key in self.server.storage:
            return self.server.storage[key]
        value = await self.server.lookup(key, value=True)
        return value

    async def set(self, key, value):
        key = int(hashlib.sha1(key).hexdigest(), 16)
        await self.server.insert(key, value)

    async def get_nearest_server(self, id):
        nodes = await self.server.lookup(id)
        return nodes[0].addr if len(nodes) > 0 else None
