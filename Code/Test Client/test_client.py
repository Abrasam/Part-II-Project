import sys, socket, json, random, time, subprocess

CHUNK_SIZE = 32

if len(sys.argv) < 2:
    print("Required arguments: <number of chunks> <clients per chunk> <range> <masterip> <masterport>")
    sys.exit(-1)

addr = (sys.argv[4], int(sys.argv[5]))

RANGE = int(sys.argv[3])

num_clients = int(sys.argv[1])

clients_per_chunk = int(sys.argv[2])

master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master.connect(addr)

master.send(json.dumps({"type":"dht"}).encode())
ok = master.recv(2)
if ok != b'ok':
    print("init failed, server down? check network?")
    sys.exit(-1)



for i in range(num_clients):
    x,y = random.randint(-RANGE,RANGE),random.randint(-RANGE,RANGE)
    master.send(b'\x00' + json.dumps((x,y)).encode())
    addr = json.loads(master.recv(1024).decode())
    print(addr)
    subprocess.Popen(["python", "test_client_auxillary.py", str(clients_per_chunk), addr["ip"], str(addr["port"]), str(x), str(y)])
    time.sleep(20)
print("wub")
