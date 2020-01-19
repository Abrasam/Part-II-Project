from kademlia.storage import Storage
from time import monotonic


def test_store():
    storage = Storage()
    storage[1337] = "hello there"
    assert 1337 in storage
    assert storage[1337] == "hello there"
    assert storage.time[1337] <= monotonic()


def test_iter():
    storage = Storage()
    storage[1337] = "hello there"
    storage[42] = "general kenobi"
    i = 0
    for key in storage:
        if i == 0:
            assert key == 1337
            i += 1
        elif i == 1:
            assert key == 42
