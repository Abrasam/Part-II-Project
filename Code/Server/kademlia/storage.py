import time

class Storage:
    def __init__(self):
        self.data = {}
        self.time = {}

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        if key in self.data and self.data[key] == value:
            self.time[key] = time.monotonic()
            return
        self.data[key] = value
        self.time[key] = time.monotonic()

    def __delitem__(self, key):
        del self.data[key]
        del self.time[key]

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        self._keys = list(self.data.keys())
        self._i = 0
        return self

    def __next__(self):
        if self._i < len(self._keys):
            self._i += 1
            return self._keys[self._i-1]
        else:
            raise StopIteration