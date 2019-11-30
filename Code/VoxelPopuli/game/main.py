import socket
import threading

chunks = {}


class ClientThread(threading.Thread):
    def __init__(self, socket, events):
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = events

    def run(self):
        pass
