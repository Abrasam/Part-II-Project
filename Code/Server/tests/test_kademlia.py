from kademlia.node import Node
from kademlia.server import DHTServer
import sys, asyncio, time, random
ip = sys.argv[1]
base_port = int(sys.argv[2])
ns = list(map(lambda x: int(x), sys.argv[3].split(",")))


async def test():
    root = DHTServer((ip, base_port), id=0)
    await root.run()

    port = base_port
    servers = []
    res = []

    last = 1
    for n in ns:
        for i in range(n-last):
            port += 1
            s = DHTServer((ip, port))
            servers.append(s)
            await s.run(bootstrap=Node(0, (ip, base_port)))
        t = 0
        tm = time.time()
        for i in range(20):
            t += await root.server.lookup_c(random.getrandbits(160))
        tm = time.time() - tm
        res.append((n, t/20.))
        print(f"{n}\t{t/20.}\t\t{tm/20.}")
        last = n
    print(res)

asyncio.run(test())
