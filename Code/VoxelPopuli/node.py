def xor_distance(id1, id2):
    return id1 ^ id2

class Node:
    def __init__(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port
        self.storage = {}

    def _ping(self, source):
        pass

    def _find_node(self, id, source):
        pass

    def _find_value(self, id, source):
        pass

    def _store(self, key, value, source):
        pass

