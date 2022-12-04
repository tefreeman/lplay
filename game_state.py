import time
from champ import Player, Champ
from typing import List, Tuple
from screen_capture import ScreenCapture
import psutil
import numpy as np
import asyncio
from PIL import Image
import colorsys


def is_color(arr, pt, rgb) -> bool:
    res = all(arr[pt[1]][pt[0]] == rgb)
    return res

# is pt1 brighter than pt2


def is_brighter(arr, pt1, pt2) -> bool:
    r1, g1, b1 = arr[pt1[1]][pt1[0]]
    r2, g2, b2 = arr[pt2[1]][pt2[0]]
    hls1 = colorsys.rgb_to_hls(r1/255, g1/255, b1/255)
    hls2 = colorsys.rgb_to_hls(r2/255, g2/255, b2/255)
    return hls1[1] > hls2[1]


class GameState:
    north_fountain = (250, 825)
    south_fountain = (20, 1055)

    def __init__(self, screen_cap: ScreenCapture) -> None:
        self.screen_cap: ScreenCapture = screen_cap
        self.start_time = None
        self.champs: Tuple[Champ, Champ, Champ, Champ] = (
            Champ(3), Champ(2), Champ(1), Champ(0))
        self.player: Player = Player()

        self.ally_base_loc = None
        self.enemy_base_loc = None

    async def update_loop(self):
        screen_count = 0
        while True:
            if self.screen_cap.count != screen_count:
                for champ in self.champs:
                    champ.update(self.screen_cap.screen_array)
                self.player.update(self.screen_cap.screen_array)
                screen_count = self.screen_cap.count
            await asyncio.sleep(0.05)

    async def wait_game_start(self):
        while (True):
            if self.is_game_running() and self.is_ingame():
                self.start_time = time.time()
                break
            await asyncio.sleep(1.0)
        await asyncio.sleep(3.0)
        self.set_base_loc()
        await asyncio.sleep(3.0)

    def is_ingame(self) -> bool:

        black_color = (0, 0, 0)
        brown_color = (107, 85, 49)

        black_pt = (262, 1034)
        black_pt2 = (40, 820)
        brown_pt = (277, 934)

        ui_pt = (1050, 975)
        ui_color = (16, 28, 27)

        result = all([is_color(self.screen_cap.screen_array, black_pt, black_color),
                      is_color(self.screen_cap.screen_array,
                               black_pt2, black_color),
                      is_color(self.screen_cap.screen_array,
                               brown_pt, brown_color),
                      is_color(self.screen_cap.screen_array, ui_pt, ui_color)])
        return result

    def is_game_running(self) -> bool:
        if "League of Legends.exe" not in (p.name() for p in psutil.process_iter()):
            return False
        return True

    def set_base_loc(self):
        south_pt = (50, 995)
        north_pt = (193, 857)

        if (is_brighter(self.screen_cap.screen_array, south_pt, north_pt)):
            self.ally_base_loc = GameState.south_fountain
            self.enemy_base_loc = GameState.north_fountain
        else:
            self.ally_base_loc = GameState.north_fountain
            self.enemy_base_loc = GameState.south_fountain

    def get_start_time(self):
        return self.start_time
