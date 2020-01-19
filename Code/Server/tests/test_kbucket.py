from kademlia.router import KBucket
from kademlia.node import Node


def test_kbucket():
    bucket = KBucket(0, 4, 2)
    bucket.add_node(Node(0, ("",0)))
    bucket.add_node(Node(1, ("",1)))
    bucket.add_node(Node(2, ("",2)))
    assert Node(0, ("",0)) in bucket.nodes
    assert Node(1, ("",1)) in bucket.nodes
    assert Node(2, ("",2)) in bucket.replacement
    assert Node(2, ("",2)) not in bucket.nodes
    bucket.remove_node(Node(0, ("",0)))
    assert Node(0, ("",0)) not in bucket.nodes
    assert Node(0, ("",0)) not in bucket.replacement
    assert Node(2, ("", 2)) not in bucket.replacement
    assert Node(2, ("", 2)) in bucket.nodes