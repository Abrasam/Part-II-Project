from server.server import Server
from kademlia.routing import *
from kademlia.node import Node


async def test():
    k1 = Server(('0.0.0.0', 25569), id=90000000000000000000000000000000000000000000000)

    await k1.run(Node(1,('127.0.0.1', 12345)))
    print("yeet")

    while True:
        await asyncio.sleep(5)
        print(k1.server.table.buckets)
        k1.server.transport.sendto("wibble".encode(), ('127.0.0.1', 12345))

asyncio.run(test())