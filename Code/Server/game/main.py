from game.gameserver import *
from game.world import *
import socket, sys, json

if len(sys.argv) != 2:
    print("Usage: <command> <base port>")
    sys.exit()

base_port = int(sys.argv[1])

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.bind(('0.0.0.0', base_port+1))

ss.listen()

chunks = {}
loaded = {}

while True:
    s, addr = ss.accept()
    data = s.recv(1024)
    chunk_coord = tuple(json.loads(data.decode()))
    print(chunk_coord)
    if chunk_coord not in chunks:  # if chunk doesn't exist
        chunks[chunk_coord] = Chunk(*chunk_coord) # make it
    if chunk_coord not in loaded:  # if chunk not loaded then load it
        loaded[chunk_coord] = ChunkThread(chunks[chunk_coord], None)  # Second argument should be DHT.
    loaded[chunk_coord].register(ClientHandler(ClientType.PLAYER, loaded[chunk_coord], s))  # register to chunk
    s.send(b'ok')  # start normal game comms
