import json
import threading
import time
import socket
import asyncio
from collections import deque
from queue import Empty, Queue

from game.const import *
from kademlia.server import DHTServer


class ChunkThread(threading.Thread):
    def __init__(self, chunk):
        threading.Thread.__init__(self)
        self.chunk = chunk
        self.players = []
        self.clients = []
        self.done = False
        self.q = Queue()
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            if self.done:
                return
            try:
                packet_data = self.q.get(timeout=5)
                self._process_packet(*packet_data)
            except Empty:
                pass

    def _process_packet(self, packet, sender):
        if packet["type"] == PacketType.PLAYER_REGISTER.value:
            sender.send(self.chunk.encode())
        if packet["type"] == PacketType.PLAYER_MOVE.value:
            for c in self.clients:
                if c == sender: continue
                c.send(packet)

    def register(self, client):
        self.clients.append(client)

    def deregister(self, client):
        self.clients.remove(client)
        return len(self.clients) == 0

    def stop(self):  # maybe need a lock on this?
        self.done = True


class Client:
    def __init__(self, type, chunk_thread):
        self.type = type  # 1 = player, 2 = other server.
        self.chunk_thread = chunk_thread
        self.to_send = deque()
        self.buf = b''

    def send(self, packet):
        self.to_send.append(json.dumps(packet).encode() + b'\n')

    def recv(self, sender):
        self.chunk_thread.q.put((json.loads(self.buf.decode()), sender))
        self.buf = b''

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<type={self.type}, chunk={self.chunk_thread.chunk.location}>"
