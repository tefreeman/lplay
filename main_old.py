import asyncio
from ainput import AInput
from screen_capture import ScreenCapture
import random
import time
import psutil
from typing import List
from champ import Champ, Player


async def main():
    await asyncio.sleep(2)
    loop = asyncio.get_event_loop()
    start_time = time.time()
    hd = AInput(loop)
    targets = ["F1", "F2", "F3", "F4"]
    tid = 3
    target = targets[tid]
    await hd.press_key(target)
    i = 0

    sc = ScreenCapture()
    champs: List[Champ] = []
    player: Player = Player()

    for i in range(0, 4):
        champs.append(Champ(i))

    while True:
        if "League of Legends.exe" not in (p.name() for p in psutil.process_iter()):
            break
        sc.update_screen()

        player.check_if_dead(sc.get_screen())

        if player.is_dead is True:
            asyncio.sleep(1.0)
            continue

        champs[i].update_is_dead(sc.get_screen())

        if i == 10:
            await hd.release_key(target)
            await asyncio.sleep(0.5)
            await hd.press_key(target)
            i = 0
        if time.time() - start_time > 400:
            start_time = time.time()
            tar_num = random.random() * 4
            if tar_num < 1.0:
                tid = 0
            elif tar_num < 2.0:
                tid = 1
            elif tar_num < 3.0:
                tid = 2
            else:
                tid = 3

            target = targets[tid]
        await hd.press_key(target)
        r_add = random.random() * 10
        r_cast = random.random() * 28
        s_cast = random.random() * 60
        r_spell = random.random() * 4
        c_type = random.random() * 10
        add_time = 1
        if r_add > 9:
            add_time = 0
        r_num = random.random() * 1 + add_time
        await asyncio.sleep(r_num)
        #r_x = (random.random() - 0.5) * 200 + 100
        #r_y = (random.random() - 0.5) * 200 + 100

        r_x = random.random() * -100 - 100
        r_y = (random.random() - 0.5) * 200
        await hd.move_mouse((r_x + 960, r_y + 540))
        if c_type < 5:
            await hd.mouse_click()
        else:
            await hd.mouse_click('right')

        if r_cast > 26:
            if r_spell <= 1.0:
                await hd.press_and_release_key("q")
            elif r_spell <= 2.0:
                await hd.press_and_release_key("w")
            elif r_spell <= 3.0:
                await hd.press_and_release_key("e")
            else:
                await hd.press_and_release_key("r")

        if s_cast > 58:
            r = random.random()
            if r > 0.5:
                await hd.press_and_release_key("d")
            else:
                await hd.press_and_release_key("f")
        elif s_cast > 45:
            await hd.press_and_release_key("ctrl+r")
            await hd.press_and_release_key("ctrl+q")
            await hd.press_and_release_key("ctrl+w")
            await hd.press_and_release_key("ctrl+e")
        i += 1


if __name__ == "__main__":
    #logger.add("spam.log", level="DEBUG")
    asyncio.run(main())
