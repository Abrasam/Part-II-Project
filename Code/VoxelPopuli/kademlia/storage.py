import time

class Storage:
    def __init__(self):
        self.data = {}
        self.time = {}
        self.orig = {}

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        if key in self.data and self.data[key] == value:
            self.time[key] = time.time()
            return
        self.data[key] = value
        self.time[key] = time.time()
        self.orig[key] = time.time()

    def __delitem__(self, key):
        del self.data[key]
        del self.time[key]
        del self.orig[key]

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        self.keys = list(self.data.keys())
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self.keys):
            self.i += 1
            return self.keys[self.i-1]
        else:
            raise StopIteration