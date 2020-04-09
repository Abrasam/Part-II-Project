from kademlia.node import Node
from kademlia.server import DHTServer
import sys, asyncio, time
ip = sys.argv[1]
base_port = int(sys.argv[2])
n = int(sys.argv[3])

root = DHTServer((ip, base_port), id=0)

port = base_port
servers = []

for i in range(n):
    port += 1
    s = DHTServer((ip, base_port))
    servers.append(s)
    asyncio.run(s.run(bootstrap=Node(0, (ip, base_port))))

t = time.time()
for i in range(20):
    asyncio.run(root.lookup())
t = time.time() - t
print(t/20.)