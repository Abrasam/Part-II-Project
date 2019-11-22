import asyncio
from kademlia.server import KademliaServer
from kademlia.node import Node
from random import getrandbits

class Kademlia:
    def __init__(self, addr, id=getrandbits(160)):
        self.id = id
        self.server = None
        self.addr = addr

    async def run(self, bootstrap=None):
        loop = asyncio.get_running_loop()
        print(self.addr)
        transport, protocol = await loop.create_datagram_endpoint(lambda: KademliaServer(self.id), local_addr=self.addr)
        self.server = protocol
        if bootstrap is not None:
            await self.server.bootstrap(bootstrap)
