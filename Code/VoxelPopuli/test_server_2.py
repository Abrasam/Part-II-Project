from server.server import Server
from kademlia.node import Node
from kademlia.routing import *
import logging

logging.basicConfig(level=logging.DEBUG)

async def test(port):
    for i in range(0,100):
        k1 = Server(('127.0.0.1', port+i))
        await k1.run(Node(90000000000000000000000000000000000000000000000, ('127.0.0.1', 25499)))

    while True:
        await asyncio.sleep(3600)

asyncio.run(test(25500+randint(0, 100)))