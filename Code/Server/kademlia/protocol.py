import asyncio
import json
import random
import time
from kademlia.node import Node
from kademlia.router import RoutingTable
from kademlia.storage import Storage

TIMEOUT = 10  # RPC timeout.
K = 20
ALPHA = 3


def stub(func):
    assert(func.__name__[:4] == "ext_")  # sanity check.

    async def rpc_stub(self, node, *args):
        loop = asyncio.get_event_loop()
        msg = {"id": random.getrandbits(32), "node": self.id, "call": True, "rpc": func.__name__[4:], "args": args}
        self.transport.sendto(json.dumps(msg).encode("UTF-8"), node.addr)
        #print("sent rpc " + json.dumps(msg) + " to " + str(node.addr) + " id: " + str(node.id))
        f = asyncio.Future()
        self.waiting[msg["id"]] = (f, loop.call_later(TIMEOUT+random.randint(0,TIMEOUT), self._timeout, msg["id"]), node)
        await f
        return f.result()
    return rpc_stub


def rpc(func):
    def rpc_func(self, *args):
        return func(self, *args)
    return rpc_func


class KademliaNode(asyncio.DatagramProtocol):
    def __init__(self, id, addr):
        self.id = id
        self.addr = addr
        self.waiting = {}
        self.transport = None
        self.table = RoutingTable(self, K)
        self.chunks = Storage()
        self.players = Storage()
        self._timeouts = {}
        self._fails = {}
        loop = asyncio.get_running_loop()

        def refresh():
            print("Refreshing stale buckets and republishing kv pairs.")
            asyncio.ensure_future(self.table.refresh_buckets(self.table.get_stale_buckets()))
            self.republish_keys()
            self.refresh = loop.call_later(3600, refresh)

        self.refresh = loop.call_later(3600, refresh)

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        print(f"we died somehow? {exc}")

    def datagram_received(self, data, addr):
        asyncio.ensure_future(self._handle_datagram(data, addr))

    def error_received(self, exc: Exception):
        print(exc)

    async def _handle_datagram(self, data, addr):
        msg = json.loads(data.decode("UTF-8"))
        #print("received " + str(msg) + " at " + str(self.id))
        node = self.table.get_node_if_contact(msg["node"])
        node = Node(msg["node"], addr) if node is None else node
        if msg["call"]:
            func = getattr(self, msg["rpc"], None)
            if func is None or not callable(func) or func.__name__ != "rpc_func":
                return
            res = json.dumps(
                {"id": msg["id"], "node": self.id, "call": False, "rpc": msg["rpc"], "ret": func(*msg["args"])})
            #print("return to sender " + res + " " + str(node.id))
            self.transport.sendto(res.encode("UTF-8"), addr)
        else:
            if msg["id"] in self.waiting:
                self.waiting[msg["id"]][1].cancel()
                self.waiting[msg["id"]][0].set_result(msg["ret"])
                del self.waiting[msg["id"]]
        self._process_contact(node)

    def _process_contact(self, node):
        self._fails[node.id] = 0
        if node.id == self.id:
            return

        # send values that need to be sent.
        if self.table.get_node_if_contact(node.id) is not None:  # if node is not new then there's nawt to do.
            return

        self.table.add_contact(node)

        # send all values it needs
        for key in self.chunks:
            nearby = self.table.nearest_nodes_to(key)
            if len(nearby) > 0:
                if not (node.id ^ key < nearby[-1].id ^ key and self.id ^ key < nearby[0].id ^ key):
                    continue
            asyncio.ensure_future(self.ext_store_chunk(node, key, self.chunks[key]))

    def _timeout(self, msg_id):
        node = self.waiting[msg_id][2]
        print("RPC call timed out to " + str(node.id) + "(" + str(node.addr) + ") from " + str(self.id) + " msgid: " + str(msg_id))
        self.waiting[msg_id][0].set_result(None)
        del self.waiting[msg_id]
        if node.id not in self._fails:
            self._fails[node.id] = 0
        self._fails[node.id] = self._fails[node.id] + 1
        if self._fails[node.id] >= 5:
            self.table.remove_contact(node)  # this is not correct to kademlia implementation, need to add 5 failure removal
        print("timed out done now yeet")
        self._timeouts[node] = time.monotonic()

    @stub
    async def ext_ping(self, node):
        pass

    @stub
    async def ext_find_node(self, node, node_id):
        pass

    @stub
    async def ext_find_chunk(self, node, key):
        pass

    @stub
    async def ext_find_player(self, node, key):
        pass

    @stub
    async def ext_store_chunk(self, node, key, value):
        pass

    @stub
    async def ext_store_player(self, node, key, value):
        pass

    @rpc
    def ping(self):
        return self.id

    @rpc
    def find_node(self, node_id):
        return list(map(lambda node: (node.id, node.addr[0], node.addr[1]), self.table.nearest_nodes_to(node_id)))

    @rpc
    def find_chunk(self, key):
        if key in self.chunks:
            return self.chunks[key]
        return self.find_node(key)

    @rpc
    def find_player(self, key):
        if key in self.players:
            return self.players[key]
        return self.find_node(key)

    @rpc
    def store_chunk(self, key, value):
        self.chunks[key] = value

    @rpc
    def store_player(self, key, value):
        self.players[key] = value

    async def lookup(self, key_or_id, value=False, find_type=None):
        nodes = self.table.nearest_nodes_to(key_or_id) + [Node(self.id,self.addr)]
        queried = [Node(self.id, self.addr)]
        found_new = False
        while len(nodes) > 0:
            best = nodes[0]
            multicast = []
            unqueried = list(filter(lambda n: n not in queried and (n not in self._timeouts or time.monotonic() - self._timeouts[n] > 600), nodes)) # don't query recently failed nodes
            for i in range(0, min(ALPHA if found_new else K, len(unqueried))):
                multicast.append(unqueried.pop(0))
            res = await asyncio.gather(*[find_type(n, key_or_id) if value else self.ext_find_node(n, key_or_id) for n in multicast])
            queried += multicast
            for i in range(0, len(res)):
                if res[i] is None:
                    continue
                if value and type(res[i]) != list:  # this means we cannot store lists in DHT.
                    return res[i]  # have found value, return it.
                nodes += list(map(lambda x: self.table.get_node_if_contact(x[0]) if self.table.get_node_if_contact(x[0]) is not None else Node(x[0], (x[1], x[2])), res[i]))
            nodes = list(set(nodes))
            nodes.sort(key=lambda n: n.id ^ key_or_id)
            nodes = nodes[:K]  # only keep K best.
            found_new = (best != nodes[0])
            if found_new or len(list(filter(lambda x: x not in queried, nodes))) > 0:
                continue
            break
        return None if value else nodes

    async def lookup_count(self, key_or_id, value=False, find_type=None):
        nodes = self.table.nearest_nodes_to(key_or_id)
        queried = [Node(self.id, ())]
        found_new = False
        while len(nodes) > 0:
            best = nodes[0]
            multicast = []
            unqueried = list(filter(
                lambda n: n not in queried and (n not in self._timeouts or time.monotonic() - self._timeouts[n] > 600),
                nodes))  # don't query recently failed nodes
            for i in range(0, min(ALPHA if found_new else K, len(unqueried))):
                multicast.append(unqueried.pop(0))
            res = await asyncio.gather(
                *[find_type(n, key_or_id) if value else self.ext_find_node(n, key_or_id) for n in multicast])
            queried += multicast
            for i in range(0, len(res)):
                if res[i] is None:
                    continue
                if value and type(res[i]) != list:  # this means we cannot store lists in DHT.
                    return res[i]  # have found value, return it.
                nodes += list(map(lambda x: self.table.get_node_if_contact(x[0]) if self.table.get_node_if_contact(
                    x[0]) is not None else Node(x[0], (x[1], x[2])), res[i]))
            nodes = list(set(nodes))
            nodes.sort(key=lambda n: n.id ^ key_or_id)
            nodes = nodes[:K]  # only keep K best.
            found_new = (best != nodes[0])
            if found_new or len(list(filter(lambda x: x not in queried, nodes))) > 0:
                continue
            break
        return len(queried)

    async def insert(self, key, value, store_type=None):
        nodes = await self.lookup(key)
        await asyncio.gather(*[store_type(n, key, value) for n in nodes])

    async def bootstrap(self, node):
        self.table.add_contact(node)
        await self.lookup(self.id)
        await self.table.refresh_buckets(self.table.buckets[i] for i in range(self.table.get_first_nonempty_bucket()+1, len(self.table.buckets)))  # should this be different?

    def republish_keys(self):
        now = time.monotonic()
        for key in self.chunks:
            value = self.chunks[key]
            t = self.chunks.time[key]
            if now - t > 3600:
                del self.chunks[key]
                asyncio.ensure_future(self.insert(key, value, store_type=self.ext_store_chunk))
        for key in self.players:
            value = self.players[key]
            t = self.players.time[key]
            if now - t > 3600:
                del self.players[key]
                asyncio.ensure_future(self.insert(key, value, store_type=self.ext_store_player))
