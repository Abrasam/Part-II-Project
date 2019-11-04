import asyncio
import socket
import msgpack


def rpc(func):
    async def rpc_func(self, *args, sender_id=None, msg_id=None, addr=None):
        msg = msgpack.packb([sender_id, msg_id, False, None, await func(self, *args)])
        print("wibble")
        self.transport.sendto(msg, addr)
        print(addr)
    return rpc_func


class KademliaServer(asyncio.DatagramProtocol):
    def __init__(self, loop):
        self.transport = None
        self.loop = loop
        self.id = 0

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        msg = msgpack.unpackb(data)
        print(msg)
        sender_id = msg[0]
        msg_id = msg[1]
        call = msg[2]  # or response?
        rpc = msg[3]
        args = msg[4:]
        if rpc == 0:
            asyncio.ensure_future(self.ping(sender_id=sender_id, msg_id=msg_id, addr=addr))
        elif rpc == 1:
            pass
        elif rpc == 2:
            pass
        elif rpc == 3:
            pass

    @rpc
    async def ping(self):
        print("called")
        return str(self.id)


async def main():
    loop = asyncio.get_event_loop()
    transport,protocol = await loop.create_datagram_endpoint(lambda: KademliaServer(loop), local_addr=('127.0.0.1', 25565))
    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()

asyncio.run(main())