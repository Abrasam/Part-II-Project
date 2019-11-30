from server.server import Server
from kademlia.routing import *
from kademlia.node import Node
import logging, sys

logging.basicConfig(level=logging.DEBUG)


async def test():
    k1 = Server(('127.0.0.1', 25499), id=90000000000000000000000000000000000000000000000)

    await k1.run()
    print("yeet")

    def got_input():
        s = sys.stdin.readline()[:-1]
        if s.startswith("s"):
            s=s[2:].split(",")
            print(s)
            asyncio.ensure_future(k1.set(s[0].encode(),s[1]))
        elif s.startswith("g"):
            s=s[2:]
            print(s)
            asyncio.ensure_future(k1.get(s.encode()))

    asyncio.get_running_loop().add_reader(sys.stdin, got_input)

    while True:
        await asyncio.sleep(3600)
#        print(k1.server.table.buckets)
#        print(len(k1.server.table))

asyncio.run(test())
