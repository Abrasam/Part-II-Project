from server.server import Server
from kademlia.routing import *
from kademlia.node import Node
import logging

logging.basicConfig(level=logging.DEBUG)

async def test():
    k1 = Server(('127.0.0.1', 25570), id=90000000000000000000000000000000000000000000000)

    await k1.run()
    print("yeet")

    while True:
        await asyncio.sleep(5)
        print(k1.server.table.buckets)

asyncio.run(test())