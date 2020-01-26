import hashlib

class Node:
    def __init__(self, id, addr):
        self.id = id
        self.addr = addr

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return "Node("+str(self.id)+")"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.id