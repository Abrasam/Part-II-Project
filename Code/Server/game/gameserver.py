import json
import threading
import time
import socket
import asyncio
from queue import Queue

from game.const import *
from kademlia.server import DHTServer


class ChunkThread(threading.Thread):
    def __init__(self, chunk):
        threading.Thread.__init__(self)
        self.chunk = chunk
        self.players = []
        self.clients = []
        self.q = Queue()
        self.lock = threading.Lock()
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            packet_data = self.q.get()
            self._process_packet(*packet_data)

    def _process_packet(self, packet, sender):
        if packet["type"] == PacketType.PLAYER_REGISTER.value:
            sender.send(self.chunk.encode())

    def register(self, client):
        self.lock.acquire()
        self.clients.append(client)
        self.lock.release()

    def deregister(self, client):
        self.lock.acquire()
        self.clients.remove(client)
        self.lock.release()


class Client:
    def __init__(self, type, chunk_thread):
        self.type = type  # 1 = player, 2 = other server.
        self.chunk_thread = chunk_thread
        self.to_send = Queue()
        self.buf = b''

    def send(self, packet):
        self.to_send.put(json.dumps(packet).encode() + b'\n')

    def recv(self, sender):
        self.chunk_thread.q.put((json.loads(self.buf.decode()), sender))
        self.buf = b''

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<type={self.type}, chunk={self.chunk_thread.chunk.location}>"
