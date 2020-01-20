from kademlia.storage import Storage
from time import monotonic
import unittest


class TestStorage(unittest.TestCase):
    def test_store(self):
        storage = Storage()
        storage[1337] = "hello there"
        self.assertTrue(1337 in storage)
        self.assertTrue(storage[1337] == "hello there")
        self.assertTrue(storage.time[1337] <= monotonic())

    def test_iter(self):
        storage = Storage()
        storage[1337] = "hello there"
        storage[42] = "general kenobi"
        i = 0
        for key in storage:
            if i == 0:
                self.assertTrue(key == 1337)
                i += 1
            elif i == 1:
                self.assertTrue(key == 42)
