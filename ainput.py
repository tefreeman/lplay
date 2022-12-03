import keyboard as kb
import mouse as mo
import asyncio
import functools
from gen_mouse import wind_mouse
import math


class AInput:
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop

    async def press_and_release_key(self, keys, delay=None):
        if delay:
            self.loop.call_later(delay, kb.press_and_release, keys)
        else:
            self.loop.call_soon(kb.press_and_release, keys)

    async def press_key(self, keys, delay=None):
        if delay:
            self.loop.call_later(delay, kb.press, keys)
        else:
            self.loop.call_soon(kb.press, keys)

    async def release_key(self, keys, delay=None):
        if delay:
            self.loop.call_later(delay, kb.release, keys)
        else:
            self.loop.call_soon(kb.release, keys)

    async def write_keys(self, text, delay=0.05):
        self.loop.call_soon(kb.write, text, delay)

    async def mouse_click(self, button='left', delay=None):
        if delay:
            self.loop.call_later(delay, mo.click, button)
        else:
            self.loop.call_soon(mo.click, button)

    async def move_mouse(self, target):
        m_pos = mo.get_position()
        await wind_mouse(m_pos[0], m_pos[1], target[0], target[1],
                         move_mouse=mo.move)
