import sys, socket, json, random, time

if len(sys.argv) < 2:
    print("Required arguments: <number of clients> <node ip> <node port>")
    sys.exit(-1)

CHUNK_SIZE = 32

num_clients = int(sys.argv[1])
addr = (sys.argv[2], int(sys.argv[3]))
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
            self.server.send(json.dumps({"type":1,"args":[CHUNK_SIZE*self.x,CHUNK_SIZE*self.y],"player":f"testplayer{self.id}"}).encode() + b'\n')
        try:
            self.server.recv(102400)
        except:
            pass
        self.server.send(json.dumps({"type":3,"args":[CHUNK_SIZE*self.x+CHUNK_SIZE/2+random.randint(-CHUNK_SIZE/4,CHUNK_SIZE/4),CHUNK_SIZE+1,CHUNK_SIZE*self.y+CHUNK_SIZE/2+random.randint(-CHUNK_SIZE/4,CHUNK_SIZE/4),random.random()*3.14],"player":f"testplayer{self.id}"}).encode() + b'\n')

for i in range(num_clients):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    s.send(json.dumps({"type":"generate","chunk":(i,0)}).encode())
    ok = s.recv(2)
    s.close()

    if ok == b'ok':
        print(f"Successfully generated chunk ({i},0).")
    ii = random.getrandbits(16)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    s.send(json.dumps({"type":"connect","player":f"{ii}","chunk":(i,0)}).encode())
    ok = s.recv(2)
    if ok != b'ok':
        print("Error",file=sys.stderr)
    else:
        clients.append(Client(0,0,ii,s))
while True:
    for c in clients:
        c.update()
    time.sleep(1/20.)
