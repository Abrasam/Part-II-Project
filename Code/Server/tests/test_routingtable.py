from kademlia.router import KBucket
from kademlia.router import RoutingTable
from kademlia.node import Node
from random import getrandbits
import asyncio
import unittest


class DummyServer:
    def __init__(self, id=getrandbits(160)):
        self.id = id

    async def ext_ping(self, *args):
        pass

    async def lookup(self, *args):
        pass


class TestRoutingTable(unittest.TestCase):
    def test_table_contacts(self):
        table = RoutingTable(DummyServer(id=0), 3)
        table.add_contact(Node(0b1111, ()))
        table.add_contact(Node(0b0001, ()))
        self.assertTrue(len(table) == 2)
        self.assertTrue(Node(0b1111, ()) == table.get_node_if_contact(0b1111))
        self.assertTrue(table.get_first_nonempty_bucket() == 0)
        self.assertTrue(table.nearest_nodes_to(1) == [Node(0b0001, ()), Node(0b1111, ())])
        self.assertTrue(len(table.buckets[0]) == 1)
        self.assertTrue(len(table.buckets[3]) == 1)
        table.remove_contact(Node(0b0001, ()))
        table.remove_contact(Node(0b01000101, ()))  # test removing node that's not in
        self.assertTrue(len(table) == 1)
        self.assertTrue(table.nearest_nodes_to(1) == [Node(0b1111,())])
        self.assertTrue(len(table.buckets[0]) == 0)
        self.assertTrue(len(table.buckets[3]) == 1)
        table = RoutingTable(DummyServer(id=0), 3)
        self.assertTrue(table.nearest_nodes_to(1) == [])

