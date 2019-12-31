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
    def __init__(self, chunk : Chunk):
        threading.Thread.__init__(self)
        self.chunk = chunk
        self.players = []
        self.clients = []
        self.done = False
        self.q = Queue()
        self.setDaemon(True)
        self.start()

    # todo: concurrency issues here with editing players/clients.
    def run(self):
        while True:
            t = time.time()
            if self.done:
                return
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
            time.sleep(max(0,TICK_LENGTH - (time.time() - t)))

    def _process_packet(self, packet, sender):
        if packet["type"] == PacketType.PLAYER_REGISTER.value:
            if sender not in self.players:
                self.players.append(sender)
                for c in self.clients:
                    if c == sender: continue
                    c.send(packet)
        elif packet["type"] == PacketType.PLAYER_DEREGISTER.value:
            if sender in self.players:
                self.players.remove(sender)
                for c in self.clients:
                    if c == sender: continue
                    c.send(packet)
                    print(c)
        elif packet["type"] == PacketType.PLAYER_MOVE.value:
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

    def register(self, client):
        self.clients.append(client)
        client.send(self.chunk.encode())
        for p in self.players:
            if p == client: continue
            client.send(Packet(PacketType.PLAYER_REGISTER, self.chunk.location, player=p.player).dict())

    def deregister(self, client):
        self.clients.remove(client)
        if client in self.players:
            self.q.put((Packet(PacketType.PLAYER_DEREGISTER, self.chunk.location, player=client.player).dict(), client))
        return len(self.clients) == 0

    def stop(self):  # maybe need a lock on this?
        self.done = True


class Client:
    def __init__(self, type, chunk_thread, player):
        self.type = type  # 1 = player, 2 = other server.
        self.chunk_thread = chunk_thread
        self.player = player
        self.to_send = deque()
        self.buf = b''

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
        return f"<type={self.type}, chunk={self.chunk_thread.chunk.location}, player={self.player}>"


class Packet:
    def __init__(self, type : PacketType, args, player=""):
        self.type = type
        self.args = args
        self.player = player

    def encode(self):
        return json.dumps({"type":self.type.value, "args": self.args, "player":self.player}).encode()

    def dict(self):
        return {"type": self.type.value, "args": self.args, "player":self.player}


