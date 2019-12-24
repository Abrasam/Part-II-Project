from kademlia.server import DHTServer
from kademlia.router import *
import logging, sys

logging.basicConfig(level=logging.DEBUG)


async def test():
    k1 = DHTServer(('127.0.0.1', 25499), id=90000000000000000000000000000000000000000000000)

    await k1.run()
    print("yeet")

    while True:
        await asyncio.sleep(3600)
#        print(k1.server.table.buckets)
#        print(len(k1.server.table))

asyncio.run(test())
