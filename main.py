import asyncio
from ainput import AInput
from screen_capture import ScreenCapture
from game_state import GameState
import random
import time
import psutil
from PIL import Image
from action import Actions
from server import start_server
import keyboard


async def main():
    loop = asyncio.get_event_loop()
    hd = AInput(loop)
    sc = ScreenCapture()
    gs = GameState(sc)
    act = Actions(gs, hd, ["r", "w", "e", "q"])

    await asyncio.sleep(3)

    sc.update_screen()
    keys_server = asyncio.create_task(start_server(act))
    screen_task_loop = asyncio.create_task(sc.update_loop(8))

    await gs.wait_game_start()

    gs_task_loop = asyncio.create_task(gs.update_loop())
    action_loop = asyncio.create_task(act.play_loop(8))

    await screen_task_loop
    await gs_task_loop
    await action_loop
    await keys_server
if __name__ == "__main__":
    #logger.add("spam.log", level="DEBUG")
    asyncio.run(main())
