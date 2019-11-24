import asyncio
import hashlib
from kademlia.kademlia import KademliaServer
from kademlia.node import Node
from random import getrandbits


class Server:
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

    def kill(self):
        self.server.transport.close()
        self.server.refresh.cancel()

    async def get(self, key):
        key = int(hashlib.sha1(key).hexdigest(), 16)  # sha1 is 160 bits so useful for kademlia.
        print("wib?")
        if key in self.server.storage:
            return self.server.storage[key]
        print("wub")
        value = await self.server.lookup(key, value=True)
        return value

    async def set(self, key, value):
        if type(key) == str:
            key = key.encode()
        key = int(hashlib.sha1(key).hexdigest(), 16)
        await self.server.insert(key, value)
