import asyncio
from node import Node
from rpc import KademliaServer


class Table:
    def __init__(self, server, k):
        self.server = server
        self.buckets = {}
        self.k = k

    async def insert(self, node):
        pass