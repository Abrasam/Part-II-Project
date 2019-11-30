import socket
from threading import Thread

chunks = {}


class ClientThread(Thread):
    def __init__(self, socket, events):
        Thread.__init__(self)
        self.socket = socket
        self.queue = events

    def run(self):
        pass
