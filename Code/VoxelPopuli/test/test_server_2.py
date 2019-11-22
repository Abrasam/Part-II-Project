import asyncio
from kademlia.kademlia import Kademlia
from kademlia.node import Node
from kademlia.routing import *


async def test():
    k1 = Kademlia(('127.0.0.1', 25561))

    await k1.run(Node(5, ('127.0.0.1', 25569)))
    print("yeet")

    while True:
        print(k1.server.table.buckets)
        await asyncio.sleep(1)

asyncio.run(test())