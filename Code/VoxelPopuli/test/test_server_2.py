from server.server import Server
from kademlia.node import Node
from kademlia.routing import *


async def test(port):
    k1 = Server(('0.0.0.0', port), id=6)

    await k1.run(Node(90000000000000000000000000000000000000000000000, ('127.0.0.1', 25569)))

    while True:
        await asyncio.sleep(3600)

asyncio.run(test(25500+randint(0, 100)))