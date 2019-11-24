from server.server import Server
from kademlia.node import Node
from kademlia.routing import *


async def test(port):
    #k1 = Server(('127.0.0.1', port))

    #await k1.run(Node(90000000000000000000000000000000000000000000000, ('127.0.0.1', 25569)))

    nodes = [None for i in range(0,100)]

    for i in range(0,5):
        nodes[i] = Server(('127.0.0.1', port + i + 1), id=1025+i)
        await nodes[i].run(Node(90000000000000000000000000000000000000000000000, ('127.0.0.1', 25569)))
        await asyncio.sleep(1)

    await asyncio.sleep(5)

    nodes[4].kill()

    await asyncio.sleep(5)

    nodes[4] = Server(('127.0.0.1', port + 50 + 1), id=1025+59)
    await nodes[4].run(Node(90000000000000000000000000000000000000000000000, ('127.0.0.1', 25569)))

    while True:
        await asyncio.sleep(5)
        continue
        action = input("(g)et or (s)et: ")
        if action == "s":
            k = input("input key: ").encode()
            v = input("input value: ")
            await k1.set(k, v)
        elif action == "g":
            k = input("input key: ").encode()
            v = await k1.get(k)
            print(v)
        print(k1.server.table.buckets)

asyncio.run(test(25570))