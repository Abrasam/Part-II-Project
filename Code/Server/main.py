from game.gameserver import *
from game.world import *
from kademlia.node import Node
import socket, sys, json

class DHTThread:
    def __init__(self, socket, dht : DHTServer):
        self.socket = socket
        self.dht = dht
        self.thread = threading.Thread(target=self.mainloop)
        self.thread.setDaemon(True)
        self.thread.start()

    def mainloop(self):
        while True:
            data = self.socket.recv(1024)
            msg = json.loads(data.decode())
            #  assume is find chunk for now.
            msg = tuple(msg)
            future = asyncio.run_coroutine_threadsafe(self.dht.get_chunk(msg), dht.loop)
            addr = future.result()
            if addr is None:
                future = asyncio.run_coroutine_threadsafe(self.dht.generate_chunk(msg), dht.loop)
                addr = future.result()
            self.socket.send(addr.encode() + b'\n')


if len(sys.argv) < 2:
    print("Usage: <command> <base port> <bootstrap address> <bootstrap port>")
    sys.exit()

base_port = int(sys.argv[1])

dht = DHTServer(('0.0.0.0', base_port))
dht_ready = threading.Event()


def ctrl_loop():
    dht_ready.wait()
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind(('0.0.0.0', base_port + 1))

    ss.listen()

    chunks = {}

    loaded = {}
    clients = []

    print("initialising game server")
    while True:
        s, addr = ss.accept()
        data = s.recv(1024)
        msg = json.loads(data.decode())
        print(msg)
        if msg["type"] == "connect":
            chunk_coord = tuple(msg["chunk"])
            print(f"Client @ {addr} connecting to chunk {chunk_coord}.")
            if chunk_coord not in chunks:  # if chunk doesn't exist
                s.send(b'no')
                s.close()
            else:
                if chunk_coord not in loaded:  # if chunk not loaded then load it
                    loaded[chunk_coord] = ChunkThread(chunks[chunk_coord])
                s.send(b'ok')  # start normal game comms
                loaded[chunk_coord].register(ClientHandler(ClientType.PLAYER, loaded[chunk_coord], s))  # register to chunk
        elif msg["type"] == "generate":
            chunk_coord = tuple(msg["chunk"])
            if chunk_coord not in chunks:
                chunks[chunk_coord] = Chunk(*chunk_coord)
            s.send(b'ok')
        elif msg["type"] == "dht":
            clients.append(DHTThread(s, dht))
            s.send(b'ok')


game_server_ctrl_thread = threading.Thread(target=ctrl_loop)
game_server_ctrl_thread.setDaemon(True)
game_server_ctrl_thread.start()


async def run():
    print("initialising DHT")
    if len(sys.argv) == 4:  # have supplied bootstrap
        await dht.run(bootstrap=Node(int(sys.argv[1]), (sys.argv[2], int(sys.argv[3]))))
    else:
        await dht.run()
    dht_ready.set()
    while True:
        await asyncio.sleep(3600)

asyncio.run(run())
