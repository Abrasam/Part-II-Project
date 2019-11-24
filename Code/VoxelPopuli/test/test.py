from server.server import Server
from kademlia.node import Node
from kademlia.routing import *


async def test():
    k1 = Server(('localhost', 25565))
    k2 = Server(('localhost', 25566))

    await asyncio.ensure_future(k1.run())
    print("yeet")
    await asyncio.ensure_future(k2.run(Node(k1.id, k1.addr)))
    print("yeet")

from random import getrandbits


class TestServer:
    def __init__(self):
        self.id = getrandbits(160)

    async def find_node(self, id):
        print("called find_node")
        return

    async def ext_ping(self, node):
        print("called ext_ping")
        return

#asyncio.run(test())

addr = (None,None)

rt = RoutingTable(TestServer(), 20)

rt.add_contact(Node(1,addr))

for i in range(1, 100):
    rt.add_contact(Node(getrandbits(160), addr))
rt.add_contact(Node(rt.server.id+1,addr))
print(rt.buckets)
print(rt.server.id)
print(rt.get_node_if_contact(1))