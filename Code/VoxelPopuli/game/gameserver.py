from queue import Queue
from threading import Thread


class Game(Thread):
    def __init__(self, dht):
        Thread.__init__(self)
        self.chunks = {}
        self.dht = dht

    def run(self):
        pass