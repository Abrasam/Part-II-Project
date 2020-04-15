import sys, socket, json, random, time

if len(sys.argv) < 2:
    print("Required arguments: <number of chunks> <clients per chunk> <node ip> <node port>")
    sys.exit(-1)

CHUNK_SIZE = 32

num_chunks = int(sys.argv[1])
num_clients = int(sys.argv[2])
addr = (sys.argv[3], int(sys.argv[4]))
clients = []

class Client:
    def __init__(self,x,y,i,s):
        self.server = None
        self.x,self.y = x,y
        self.server = s
        self.id = i
        self.init = False

    def update(self):
        if not self.init:
            self.server.send(json.dumps({"type":1,"args":[CHUNK_SIZE*self.x,CHUNK_SIZE*self.y],"player":f"{self.id}"}).encode() + b'\n')
            self.init = True
        try:
            self.server.recv(1024)
        except:
            pass
        self.server.send(json.dumps({"type":3,"args":[CHUNK_SIZE*self.x+CHUNK_SIZE/2+random.randint(-CHUNK_SIZE/4,CHUNK_SIZE/4),CHUNK_SIZE+1,CHUNK_SIZE*self.y+CHUNK_SIZE/2+random.randint(-CHUNK_SIZE/4,CHUNK_SIZE/4),random.random()*3.14],"player":f"{self.id}"}).encode() + b'\n')

for i in range(num_chunks):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    s.send(json.dumps({"type":"generate","chunk":(i,0)}).encode())
    ok = s.recv(2)
    s.close()
    if ok == b'ok':
        print(f"Successfully generated chunk ({i},0).")
    for _ in range(num_clients):
        ii = random.getrandbits(16)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        s.send(json.dumps({"type":"connect","player":f"{ii}","chunk":(i,0)}).encode())
        ok = s.recv(2)
        if ok != b'ok':
            print("Error",file=sys.stderr)
        else:
            clients.append(Client(i,0,ii,s))
print(len(clients))
while True:
    for c in clients:
        c.update()
    time.sleep(1/20.)
