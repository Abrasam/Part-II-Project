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


class ClientHandler:
    def __init__(self, type, chunk_thread, socket : socket.socket):
        self.type = type  # 1 = player, 2 = other server.
        self.socket = socket
        self.q = chunk_thread.q
        self.to_send = Queue()
        self.stop = threading.Event()
        self.chunk_thread = chunk_thread
        self.chunk_thread.register(self)

        def send_loop():
            while True:
                if self.stop.is_set():
                    return
                data = self.to_send.get() + b'\n'
                print("Sending: " + str(data))
                self.socket.send(data)

        def recv_loop():
            while True:
                if self.stop.is_set():
                    return
                data = b''
                char = b''
                while char != b'\n':
                    data += char
                    char = self.socket.recv(1)

                print("Received:" + str(data))
                print(data.decode())
                self.q.put((json.loads(data.decode()), self))

        self.send_thread = threading.Thread(target=send_loop)
        self.send_thread.setDaemon(True)
        self.send_thread.start()
        self.recv_thread = threading.Thread(target=recv_loop)
        self.recv_thread.setDaemon(True)
        self.recv_thread.start()

    def send(self, data):
        self.to_send.put(data)

    def kill(self):
        self.stop.set()
        self.chunk_thread.deregister(self)

