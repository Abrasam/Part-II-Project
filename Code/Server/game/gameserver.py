import json
import threading
import time
import datetime
import socket
import asyncio
from collections import deque
from queue import Empty, Queue

from game.const import *
from game.world import Chunk
from kademlia.server import DHTServer


class ChunkThread(threading.Thread):
    def __init__(self, dht : DHTServer, chunk : Chunk):
        threading.Thread.__init__(self)
        self.chunk = chunk
        self.players = {}
        self.clients = []
        self.dht = dht
        self.done = False
        self.q = Queue()
        self.setDaemon(True)
        self.start()

    # todo: concurrency issues here with editing players/clients.
    def run(self):
        ticks = 0
        timer = 0
        while True:
            t = time.time()
            try:
                n = self.q.qsize()
                for _ in range(n):
                    packet_data = self.q.get_nowait()
                    self._process_packet(*packet_data)
            except Empty:
                pass
            for client in self.players:
                tmp = datetime.datetime.utcnow()
                client.send(Packet(PacketType.TIME, [tmp.hour*60+tmp.minute+tmp.second/60]).dict())
            for c in self.players:
                tim = time.time()
                if tim - self.players[c].touched > 5:
                    c.socket.close()
                    self.remove_client(c)
            time.sleep(max(0,TICK_LENGTH - (time.time() - t)))
            if self.done and self.q.empty():
                return
            '''ticks += 1
            timer += time.time() - t
            if timer > 5:
                print("TPS:" + str(ticks / timer))
                timer = 0
                ticks = 0'''

    def _process_packet(self, packet, sender):
        if packet["type"] == PacketType.PLAYER_REGISTER.value:
            if sender not in self.players:
                self.players[sender] = Player(sender.name, (0,0,0))
                for c in self.clients:
                    if c == sender: continue
                    c.send(packet)
        elif packet["type"] == PacketType.PLAYER_DEREGISTER.value:
            if sender in self.players:

                asyncio.run_coroutine_threadsafe(self.dht.save_player(self.players[sender].name, self.players[sender].location), self.dht.loop)
                del self.players[sender]
                for c in self.clients:
                    if c == sender: continue
                    c.send(packet)
        elif packet["type"] == PacketType.PLAYER_MOVE.value:
            if sender in self.players:
                self.players[sender].touch()
                self.players[sender].update_location(packet["args"][0:3])
                for c in self.clients:
                    if c == sender: continue
                    c.send(packet)
        elif packet["type"] == PacketType.BLOCK_CHANGE.value:
            pos = packet["args"][0:3]
            if pos in self.chunk:
                self.chunk.update(*packet["args"])
                data = json.dumps(self.chunk.encode()).encode()
                for client in self.clients:
                    client.send_raw(data)

    def add_client(self, client):
        self.clients.append(client)
        client.send(self.chunk.encode())
        for c in self.players:
            if c == client: continue
            client.send(Packet(PacketType.PLAYER_REGISTER, self.chunk.location, player=c.name).dict())

    def remove_client(self, client):
        self.clients.remove(client)
        if client in self.players:
            self.q.put((Packet(PacketType.PLAYER_DEREGISTER, self.chunk.location, player=client.name).dict(), client))
        return len(self.clients) == 0

    def stop(self):  # maybe need a lock on this?
        self.done = True


class Player:
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.touched = time.time()

    def touch(self):
        self.touched = time.time()

    def update_location(self, loc):
        self.location = loc


class Client:
    def __init__(self, type, chunk_thread, name, conn):
        self.type = type  # 1 = player, 2 = other server (not used yet).
        self.chunk_thread = chunk_thread
        self.name = name
        self.to_send = deque()
        self.buf = b''
        self.socket = conn

    def send(self, packet):
        self.to_send.append(json.dumps(packet).encode() + b'\n')

    def send_raw(self, raw_packet):
        self.to_send.append(raw_packet + b'\n')

    def recv(self, sender):
        self.chunk_thread.q.put((json.loads(self.buf.decode()), sender))
        self.buf = b''

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<type={self.type}, chunk={self.chunk_thread.chunk.location}, player={self.name}>"


class Packet:
    def __init__(self, type : PacketType, args, player=""):
        self.type = type
        self.args = args
        self.player = player

    def encode(self):
        return json.dumps({"type":self.type.value, "args": self.args, "player":self.player}).encode()

    def dict(self):
        return {"type": self.type.value, "args": self.args, "player":self.player}


