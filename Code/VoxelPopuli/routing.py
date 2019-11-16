import asyncio
import time
from node import Node
from rpc import KademliaServer


class KBucket:
    def __init__(self, lower, upper, k):
        self.range = (lower, upper)
        self.k = k
        self.updated = time.time()
        self.updated()
        self.nodes = []

    def updated(self):
        self.updated = time.time()

    def add_node(self, node):
        if node in self.nodes:
            del self.nodes[self.nodes.index(node)]
            self.nodes.append(node)
        elif len(self) < self.k:
            self.nodes.append(node)
        else:
            return False
        return True

    def remove_node(self, node):
        if node in self.nodes:
            del self.nodes[self.nodes.index(node)]

    def split(self):
        l, r = KBucket(self.lower, (self.lower+self.upper)/2, self.k), KBucket((self.lower+self.upper)/2, self.upper, self.k)
        for node in self.nodes:
            if node.id < l.upper:
                l.add_node(node)
            else:
                r.add_node(node)
        return l, r

    def __len__(self):
        return len(self.nodes)


class RoutingTable:
    def __init__(self, server, k):
        self.server = server
        self.buckets = [KBucket(0, 256, k)]
        self.k = k

    def add_contact(self, node):
        pass