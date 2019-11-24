from server.server import Kademlia
from kademlia.routing import *


async def test():
    k1 = Kademlia(('127.0.0.1', 25569),id=90000000000000000000000000000000000000000000000)

    await k1.run()
    print("yeet")

    while True:
        print(k1.server.table.buckets)
        print(len(k1.server.table))
        await asyncio.sleep(1)

asyncio.run(test())