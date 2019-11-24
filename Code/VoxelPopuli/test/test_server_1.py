from server.server import Server
from kademlia.routing import *


async def test():
    k1 = Server(('127.0.0.1', 25569), id=90000000000000000000000000000000000000000000000)

    await k1.run()
    print("yeet")

    while True:
        print(k1.server.table.buckets)
        print(len(k1.server.table))
        await asyncio.sleep(5)

asyncio.run(test())