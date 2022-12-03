import asyncio
import keyboard
from action import Actions
import mouse


class EchoServerProtocol:
    def __init__(self, act: Actions) -> None:
        self.act: Actions = act

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        key = data.decode()
        if "," in key:
            if self.act.enabled == False:
                ls = key.split(",")
                x = int(ls[0])
                y = int(ls[1])
                mouse.move(x, y)

        elif key == "kms":
            self.act.toggle_kms()
            print('Received %r from %s' % (key, addr))
        elif key == "enable":
            self.act.toggle_enabled()
            print('Received %r from %s' % (key, addr))
        elif key == "1" or key == "2" or key == "3" or key == "4":
            self.act.set_target(key)
            print('Received %r from %s' % (key, addr))
        else:
            keyboard.press_and_release(key)
            print('Received %r from %s' % (key, addr))


async def start_server(act: Actions):
    print("Starting UDP server")

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(act),
        local_addr=('192.168.1.3', 9999))

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()
