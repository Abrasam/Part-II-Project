import select
from queue import Empty

from game.gameserver import *
from game.world import *
from kademlia.node import Node
import socket, sys, json


class DHTThread:  # todo: make this gracefully die/integrate it into the select stuff
    def __init__(self, socket, dht : DHTServer):
        self.socket = socket
        self.dht = dht
        self.thread = threading.Thread(target=self.mainloop)
        self.thread.setDaemon(True)
        self.thread.start()

    def mainloop(self):
        while True:
            try:
                data = self.socket.recv(1024)
                if data:
                    msg = json.loads(data[1:].decode())
                    if data[0] == 0:
                        msg = tuple(msg)
                        future = asyncio.run_coroutine_threadsafe(self.dht.get_chunk(msg), dht.loop)
                        addr = future.result()
                        if addr is None:
                            future = asyncio.run_coroutine_threadsafe(self.dht.generate_chunk(msg), dht.loop)
                            addr = future.result()
                        self.socket.send(addr.encode() + b'\n')
                    elif data[0] == 1:
                        name = msg["name"]
                        print(f"Looking for {name}")
                        future = asyncio.run_coroutine_threadsafe(self.dht.get_player(name), self.dht.loop)
                        player = future.result()
                        if player:
                            x,y,z = player["pos"]
                            self.socket.send(json.dumps({"x":x,"y":y,"z":z}).encode())
                        else:
                            self.socket.send(json.dumps({"x":0,"y":32,"z":0}).encode())
                else:
                    self.socket.close()
                    return
            except ConnectionError:
                return


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
    ss.setblocking(0)

    ss.listen(5)

    chunks = {}
    loaded = {}

    clients = {}

    print("initialising game server")

    t = time.time()

    while True:
        if time.time() - t > 5:
            t = time.time()
            print(f"Thread Count: {threading.active_count()}")
        sockets = list(clients.keys()) + [ss]
        for s in sockets:
            if s.fileno() == -1:
                print(clients[s])
        readable, writable, exceptional = select.select(sockets, sockets, sockets)
        for r in readable:
            if r == ss:
                s, addr = ss.accept()
                s.setblocking(1)
                data = s.recv(1024)
                msg = json.loads(data.decode())
                #print(msg)
                if msg["type"] == "connect":
                    chunk_coord = tuple(msg["chunk"])
                    player = msg["player"]
                    #print(f"Client @ {addr} connecting to chunk {chunk_coord}.")
                    if chunk_coord not in chunks:  # if chunk doesn't exist
                        s.send(b'no')
                        s.close()
                    else:
                        if chunk_coord not in loaded:  # if chunk not loaded then load it
                            loaded[chunk_coord] = ChunkThread(dht, chunks[chunk_coord])
                        s.send(b'ok')  # start normal game comms
                        s.setblocking(0)
                        client = Client(ClientType.PLAYER, loaded[chunk_coord], msg["player"], s)
                        loaded[chunk_coord].add_client(client)  # register to chunk
                        clients[s] = client
                elif msg["type"] == "generate":
                    chunk_coord = tuple(msg["chunk"])
                    if chunk_coord not in chunks:
                        chunks[chunk_coord] = Chunk(*chunk_coord)
                    s.send(b'ok')
                elif msg["type"] == "dht":
                    DHTThread(s, dht)
                    s.send(b'ok')
            else:
                try:
                    data = r.recv(1024)
                    if data:
                        client = clients[r]
                        for c in [data[i:i+1] for i in range(len(data))]:
                            if c == b'\n':
                                client.recv(client)
                            else:
                                client.buf += c
                    else:
                        if clients[r].chunk_thread.remove_client(clients[r]):
                            clients[r].chunk_thread.stop()
                            del loaded[clients[r].chunk_thread.chunk.location]
                        del clients[r]
                        if r in writable:
                            writable.remove(r)
                        if r in exceptional:
                            exceptional.remove(r)
                        r.close()
                except ConnectionError:
                    pass
        for w in writable:
            client = clients[w]
            try:
                data = client.to_send.popleft()
                #print(f"Sending: {data}")
                sent = w.send(data)
                if sent != len(data):
                    client.to_send.appendleft(data[sent:])
            except IndexError:
                pass
            except ConnectionError:
                pass

        for e in exceptional:
            if clients[e].chunk_thread.remove_client(clients[e]):
                clients[e].chunk_thread.stop()
                del loaded[clients[e].chunk_thread.chunk.location]
            del clients[e]
            e.close()


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
