from kademlia.router import KBucket
from kademlia.router import RoutingTable
from kademlia.node import Node
from random import getrandbits
import asyncio


class DummyServer():
    def __init__(self, id=getrandbits(160)):
        self.id = id

    async def ext_ping(self, *args):
        pass

    async def lookup(self, *args):
        pass


def test_table_contacts():
    table = RoutingTable(DummyServer(id=0), 3)
    table.add_contact(Node(0b1111, ()))
    table.add_contact(Node(0b0001, ()))
    assert table.nearest_nodes_to(1) == [Node(0b0001, ()), Node(0b1111, ())]
    assert len(table.buckets[0]) == 1
    assert len(table.buckets[3]) == 1
    table.remove_contact(Node(0b0001, ()))
    table.remove_contact(Node(0b01000101, ()))  # test removing node that's not in
    assert table.nearest_nodes_to(1) == [Node(0b1111,())]
    assert len(table.buckets[0]) == 0
    assert len(table.buckets[3]) == 1
