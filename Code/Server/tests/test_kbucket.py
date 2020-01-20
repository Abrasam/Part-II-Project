from kademlia.router import KBucket
from kademlia.node import Node
import unittest


class TestKBucket(unittest.TestCase):
    def test_k_bucket(self):
        bucket = KBucket(0, 4, 2)
        bucket.add_node(Node(0, ("",0)))
        bucket.add_node(Node(1, ("",1)))
        bucket.add_node(Node(2, ("",2)))
        self.assertTrue(Node(0, ("",0)) in bucket.nodes)
        self.assertTrue(Node(1, ("",1)) in bucket.nodes)
        self.assertTrue(Node(2, ("",2)) in bucket.replacement)
        self.assertTrue(Node(2, ("",2)) not in bucket.nodes)
        bucket.remove_node(Node(0, ("",0)))
        self.assertTrue(Node(0, ("",0)) not in bucket.nodes)
        self.assertTrue(Node(0, ("",0)) not in bucket.replacement)
        self.assertTrue(Node(2, ("", 2)) not in bucket.replacement)
        self.assertTrue(Node(2, ("", 2)) in bucket.nodes)