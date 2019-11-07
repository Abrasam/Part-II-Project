import asyncio
import socket
import msgpack


def rpc(func):
    def rpc_func(*args, **kwargs):
        return func(*args, **kwargs)
    return rpc_func


def stub(func):
    async def rpc_stub(self, addr, *args, **kwargs):
        return await func(*args, **kwargs)
    return rpc_stub


class RPCServer(asyncio.DatagramProtocol):
    def __init__(self, loop):
        self.transport = None
        self.loop = loop
        self.id = 0

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        msg = msgpack.unpackb(data,raw=False)
        if msg["type"] == 0:
            func = getattr(self, msg["rpc"], None)
            if func is None or not callable(func) or not func.__name__ == "rpc_func":
                print("dropping invalid call")
                return
            response = msgpack.packb({"type" : 1, "id" : msg[id], "rep" : func(*msg["args"])})
            self.transport.sendto(response, addr)


class RPCClient(asyncio.DatagramProtocol):
    def __init__(self, loop):
        self.transport = None
        self.loop = loop
        self.id = 0
        self.waiting = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        msg = msgpack.unpackb(data,raw=False)
        if msg["type"] == 1:
            if msg["id"] in self.waiting:
                self.waiting[msg["id"]] = msg


async def main():
    loop = asyncio.get_event_loop()
    transport,protocol = await loop.create_datagram_endpoint(lambda: RPCServer(loop), local_addr=('127.0.0.1', 25565))
    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()

asyncio.run(main())