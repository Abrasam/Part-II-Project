from kademlia.node import Node
from kademlia.server import DHTServer
import sys, asyncio, time, random, subprocess
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

    port += 2
    goto = subprocess.Popen(['python3.8', 'main.py', ip, str(port), "-b", ip, str(base_port), "0", "-i", "83458345"])
    node_to_use = Node(83458345, (ip, base_port + 2))
    last = 1
    for n in ns:
        time.sleep(1)
        for i in range(n-last):
            port += 1
            p = subprocess.Popen(['python3.8', 'main.py', ip, str(port), "-b", ip, str(base_port), "0"])
            time.sleep(0.1)
            servers.append(p)
        counts = []
        for i in range(100):
            tm = time.time()
            await root.server.ext_ping(node_to_use)
            tm = time.time() - tm
            counts.append(tm)
        mu = sum(counts)/100.
        res.append((n, mu))
        sigma = (sum(map(lambda x: (x - mu)**2, counts))/100)**0.5
        errs.append((n, sigma))
        print(f"{n}\t{mu}\t\t{sigma}")
        last = n
    print(res)
    print(errs)
    for p in servers:
        p.kill()
    goto.kill()

asyncio.run(test())
