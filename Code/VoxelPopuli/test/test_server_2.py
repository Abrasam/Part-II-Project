from server.server import Kademlia
from kademlia.node import Node
from kademlia.routing import *


async def test(port):
    k1 = Kademlia(('127.0.0.1', port))

    await k1.run(Node(90000000000000000000000000000000000000000000000, ('127.0.0.1', 25569)))

    nodes = [None for i in range(0,100)]

    for i in range(0,0):
        nodes[i] = Kademlia(('127.0.0.1', port+i+1))
        await nodes[i].run(Node(5, ('127.0.0.1', 25569)))

    await asyncio.sleep(10)

    while True:
        action = input("(g)et or (s)et: ")
        if action == "s":
            k = input("input key: ").encode()
            v = input("input value: ")
            await k1.set(k, v)
        elif action == "g":
            k = input("input key: ").encode()
            v = await k1.get(k)
            print(v)
        await asyncio.sleep(5)

asyncio.run(test(25570))