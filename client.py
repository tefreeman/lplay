import asyncio
import keyboard
import mouse
from key_map import keyboard_keys, mouse_keys


class EchoClientProtocol:
    def __init__(self, on_con_lost):
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        pass

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Connection closed")
        self.on_con_lost.set_result(True)


def send_func(transport, key: str):
    transport.sendto(key.encode())


async def start_client():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoClientProtocol(on_con_lost),
        remote_addr=('192.168.1.3', 9999))

    for key, val in keyboard_keys.items():
        keyboard.add_hotkey(key, send_func, args=(transport, val))

    for key, val in mouse_keys.items():
        mouse.on_button(send_func, args=(transport, val),
                        buttons=key, types='up')
    old_pos = (-1, -1)
    while True:
        await asyncio.sleep(0.025)
        pos = mouse.get_position()

        if pos != old_pos:
            old_pos = pos
            send_func(transport, str(pos[0])+"," + str(pos[1]))
    try:
        await on_con_lost
    finally:
        transport.close()

if __name__ == "__main__":
    #logger.add("spam.log", level="DEBUG")
    asyncio.run(start_client())
