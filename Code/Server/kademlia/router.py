import asyncio
import time
from random import randint


class KBucket:
    def __init__(self, lower, upper, k):
        self.lower, self.upper = lower, upper
        self.k = k
        self.updated = time.monotonic()
        self.update()
        self.nodes = []
        self.replacement = []

    def update(self):
        self.updated = time.monotonic()

    def add_node(self, node):
        if node in self.nodes:
            del self.nodes[self.nodes.index(node)]
            self.nodes.append(node)
        elif len(self) < self.k:
            self.nodes.append(node)
        else:
            if node in self.replacement:
                del self.replacement[self.replacement.index(node)]
            self.replacement.append(node)
            return False
        return True

    def remove_node(self, node):
        if node in self.replacement:
            del self.replacement[self.replacement.index(node)]

        if node in self.nodes:
            del self.nodes[self.nodes.index(node)]

            if len(self.replacement) > 0:
                #print("added from replacement " + str(self.replacement[-1]))
                self.add_node(self.replacement.pop())  # this may not accurately do LRU entirely correctly.

    def __len__(self):
        return len(self.nodes)

    def __str__(self):
        return "KBucket("+str(self.nodes)+")" if len(self) > 0 else ""

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.nodes[item]


class RoutingTable:
    def __init__(self, server, k):
        self.server = server
        self.buckets = [KBucket(2**i, 2**(i+1), k) for i in range(0, 160)]
        self.k = k

    def get_bucket(self, id):
        for i in range(0, len(self.buckets)):
            if self.buckets[i].lower <= id ^ self.server.id < self.buckets[i].upper:
                return i
        return None  # should get be here.

    def add_contact(self, node):
        if node.id == self.server.id:
            raise RuntimeError()
        i = self.get_bucket(node.id)
        if self.buckets[i].add_node(node):
            return
        asyncio.ensure_future(self.server.ext_ping(self.buckets[i][0]))  # call ping to force staleness check.

    def remove_contact(self, node):
        i = self.get_bucket(node.id)
        self.buckets[i].remove_node(node)

    def nearest_nodes_to(self, key):
        candidates = [node for bucket in self.buckets for node in bucket]
        candidates.sort(key=lambda x: x.id ^ key)
        return candidates[:self.k]

    def get_stale_buckets(self):
        now = time.monotonic()
        return list(filter(lambda b: (now - b.updated > 3600), self.buckets))

    def refresh_buckets(self, buckets):
        return asyncio.gather(*[self.server.lookup(randint(b.lower, b.upper)) for b in buckets])

    def get_node_if_contact(self, node_id):
        if node_id == self.server.id: return None
        buckets = list(filter(lambda b: b.id == node_id, self.buckets[self.get_bucket(node_id)].nodes))
        if len(buckets) == 1:
            return buckets[0]
        else:  # should never be anything other than 1 or 0 so treat >1 as failure case as something sure is wrong there
            return None

    def get_first_nonempty_bucket(self):
        for i in range(0,len(self.buckets)):
            if len(self.buckets[i]) > 0:
                return i
        return -1

    def __len__(self):
        return sum(map(lambda b: len(b.nodes), self.buckets))
