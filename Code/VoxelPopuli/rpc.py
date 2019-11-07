import asyncio
import json
import socket
import random
from node import Node


TIMEOUT = 10  # RPC timeout.


def stub(func):
    async def rpc_stub(self, *args):
        loop = asyncio.get_event_loop()
        msg = json.dumps({"id": random.getrandbits(32), "node": self.id, "call": True, "rpc": func.__name__, "arg": args})
        self.socket.sendto(msg.encode("UTF-8"), self.addr)
        f = asyncio.Future()
        self.waiting[msg["id"]] = (f, loop.call_later(TIMEOUT, self._timeout, msg["id"]))
        await f
        return f.result()
    return rpc_stub


def rpc(func):
    def rpc_func(self, *args):
        return func(self, *args)
    return rpc_func


class KademliaServer:
    def __init__(self, node_id, addr):
        self.id = node_id
        self.addr = addr
        self.waiting = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(addr)

    async def run(self):
        while True:
            data,addr = self.socket.recvfrom(1024)
            msg = json.loads(data.decode("UTF-8"))
            node = Node(msg["node"], addr)
            if msg["call"]:
                func = getattr("_"+msg["rpc"], None)
                if func is None or not callable(func) and func.__name__ == "rpc_func":
                    continue
                res = json.dumps({"id": msg["id"], "node": self.id, "call": False, "rpc": msg["rpc"], "ret": func(*msg["args"], node)})
                self.socket.sendto(res.encode("UTF-8"), addr)
            else:
                if msg["id"] in self.waiting:
                    self.waiting[msg["id"]][1].cancel()
                    self.waiting[msg["id"]][0].set_result((True, msg["ret"]))
                    del self.waiting[msg["id"]]

    async def _timeout(self, msg_id):
        self.waiting[msg_id][0].set_result((False, None))
        del self.waiting[msg_id]

    @stub
    async def ping(self):
        pass

    @stub
    async def find_node(self, node_id):
        pass

    @stub
    async def find_value(self, key):
        pass

    @stub
    async def store(self, key, value):
        pass

    @rpc
    def _ping(self, source):
        pass

    @rpc
    def _find_node(self, node_id, source):
        pass

    @rpc
    def _find_value(self, key, source):
        pass

    @rpc
    def _store(self, key, value, source):
        pass
