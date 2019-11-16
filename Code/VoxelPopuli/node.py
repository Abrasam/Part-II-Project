class Node:
    def __init__(self, id, addr):
        self.id = id
        self.addr = addr
        self.fails = 0

    def stale(self):
        return self.fails >= 5