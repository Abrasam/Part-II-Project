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
    errs = []

    last = 1
    for n in ns:
        for i in range(n-last):
            port += 1
            s = DHTServer((ip, port))
            servers.append(s)
            await s.run(bootstrap=Node(0, (ip, base_port)))
        counts = []
        tm = time.time()
        for i in range(100):
            counts.append(await root.server.lookup_count(random.getrandbits(160)))
        tm = time.time() - tm
        mu = sum(counts)/100.
        res.append((n, mu))
        sigma = (sum(map(lambda x: (x - mu)**2, counts))/100)**0.5
        errs.append((n, sigma))
        print(f"{n}\t{mu}\t\t{sigma}\t\t\t{tm/20.}")
        last = n
    print(res)
    print(errs)

asyncio.run(test())
