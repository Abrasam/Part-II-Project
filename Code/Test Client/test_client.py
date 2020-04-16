import sys, socket, json, random, time

CHUNK_SIZE = 32

if len(sys.argv) < 2:
    print("Required arguments: <number of clients> <range> <node ip> <node port>")
    sys.exit(-1)

RANGE = int(sys.argv[2])

class Client:
    def __init__(self,x,y,i):
        self.current = None
        self.x,self.y = x,y
        self.id = i
        self.init = False

    def update(self):
        if not self.init:
            self.current.send(json.dumps({"type":1,"args":[self.x,self.y],"player":f"testplayer{self.id}"}).encode() + b'\n')
        try:
            self.current.recv(102400)
        except:
            pass
        self.current.send(json.dumps({"type":3,"args":[CHUNK_SIZE*self.x+CHUNK_SIZE/2+random.randint(-CHUNK_SIZE/4,CHUNK_SIZE/4),CHUNK_SIZE+1,CHUNK_SIZE*self.y+CHUNK_SIZE/2+random.randint(-CHUNK_SIZE/4,CHUNK_SIZE/4),0],"player":f"testplayer{self.id}"}).encode() + b'\n')

    def move(self):
        self.init = False
        if self.current:
            self.current.send(json.dumps({"type":2,"args":[self.x,self.y],"player":f"testplayer{self.id}"}).encode() + b'\n')
            self.current.close()
        self.x,self.y=random.randint(-RANGE,RANGE),random.randint(-RANGE,RANGE)
        master.send(b'\x00' + json.dumps((self.x,self.y)).encode())
        addr = json.loads(master.recv(1024).decode())
        addr = (addr["ip"],addr["port"])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        s.send(json.dumps({"type":"connect","chunk":(self.x,self.y),"player":f"testplayer{self.id}"}).encode())
        resp = s.recv(2)
        if resp == b'no':
            print("Server rejected connect attempt.")
        elif resp == b'ok':
            self.current = s
            s.settimeout(1/20)
            print(f"Successfully connected to {(self.x,self.y)}.")
        else:
            print("Some funky shit happening here.")
          
num_clients = int(sys.argv[1])
addr = (sys.argv[3], int(sys.argv[4]))

master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master.connect(addr)

master.send(json.dumps({"type":"dht"}).encode())
ok = master.recv(2)
if ok != b'ok':
    print("init failed, server down? check network?")
    sys.exit(-1)

clients = []

for i in range(num_clients):
    print(f"[{i}/{num_clients}] ",end="")
    c = Client(0,0,random.randint(0,500)*i)
    c.move()
    clients.append(c)

while True:
    for i in range(num_clients):
        clients[i].update()
        if random.random() < 0.01 and random.random() < 0.1:
            clients[i].move()
    time.sleep(1/20)
    print("iter")
