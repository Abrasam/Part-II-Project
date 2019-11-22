import asyncio
import time
from random import randint


class KBucket:
    def __init__(self, lower, upper, k):
        self.lower, self.upper = lower, upper
        self.k = k
        self.updated = time.time()
        self.update()
        self.nodes = []
        self.replacement = []

    def update(self):
        self.updated = time.time()

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
                self.add_node(self.replacement.pop())  # this may not accurately do LRU.

    def split(self):
        l, r = KBucket(self.lower, (self.lower+self.upper)/2, self.k), KBucket((self.lower+self.upper)/2, self.upper, self.k)
        for node in (self.nodes + self.replacement):
            if node.id < l.upper:
                l.add_node(node)
            else:
                r.add_node(node)
        return l, r

    def __len__(self):
        return len(self.nodes)

    def __str__(self):
        return "KBucket("+str(self.nodes)+")"

    def __repr__(self):
        return self.__str__()


class RoutingTable:
    def __init__(self, server, k):
        self.server = server
        self.buckets = [KBucket(0, 2**160, k)]
        self.k = k

    def get_bucket(self, id):
        for i in range(0, len(self.buckets)):
            if self.buckets[i].lower <= id < self.buckets[i].upper:
                return i
        return None  # should get be here.

    def add_contact(self, node):
        i = self.get_bucket(node.id)
        if self.buckets[i].add_node(node):
            return

        if self.buckets[i].lower <= self.server.id < self.buckets[i].upper:
            # if bucket has range of current node then split.
            l, r = self.buckets[i].split()
            self.buckets[i] = l
            self.buckets.insert(i+1, r)
            self.add_contact(node)
        else:  # no need to check if self.buckets[0] exists cause if it didn't then we would not be here.
            asyncio.ensure_future(self.server.ext_ping(self.buckets[0]))  # call ping to force staleness check.

    def remove_contact(self, node):
        i = self.get_bucket(node.id)
        self.buckets[i].remove_node(node)

    def nearest_nodes_to(self, node_id):
        i = self.get_bucket(node_id)
        j = 1
        self.buckets[i].update()
        candidates = self.buckets[i].nodes[:]
        print(candidates)
        print(len(self.buckets))
        while len(candidates) < self.k and (0 <= i-j < len(self.buckets) or 0 <= i+j < len(self.buckets)):
            print(i-j)
            print(i+j)
            print(len(self.buckets))
            if 0 <= i-j < len(self.buckets):
                candidates += self.buckets[i-j].nodes[:]
            if 0 <= i+j < len(self.buckets):
                candidates += self.buckets[i+j].nodes[:]
            j += 1
        candidates = list(filter(lambda x: x.id != node_id, candidates))
        candidates.sort(key=lambda x: x.id ^ node_id)
        return candidates[:self.k]

    def refresh_buckets(self):
        now = time.time()
        stale = list(filter(lambda b: now - b.updated > 60*60, self.buckets))
        for b in stale:
            random_id = randint(b.lower, b.upper)
            asyncio.ensure_future(self.server.find_node(random_id))

    def get_node_if_contact(self, node_id):
        buckets = list(filter(lambda b: b.id == node_id, self.buckets[self.get_bucket(node_id)].nodes))
        if len(buckets) == 1:
            return buckets[0]
        else:  # should never be anything other than 1 or 0 so treat >1 as failure case as something sure is wrong there
            return None

