from game_state import GameState
from typing import List
import time
import keyboard
import asyncio
from ainput import AInput


class Actions:
    def __init__(self, gs: GameState, hd: AInput, spell_list: List[str]) -> None:
        self.enabled = True
        self.kms = False
        self.screen_center = (955, 500)
        self.gs: GameState = gs
        self.spell_list: List[str] = spell_list
        self.level = 0
        self.target = 4
        self.hd: AInput = hd
        self.prev = {
            "learn_spell": 0,
            "auto_heal": 0
        }

    def set_target(self, tar: str):
        keyboard.release("f" + str(self.target))
        self.target = int(tar)
        keyboard.press_and_release("w")

    def toggle_kms(self):
        self.kms = not self.kms

    def toggle_enabled(self):
        self.enabled = not self.enabled
        print("done")

    async def try_learn_spell(self, min_wait_time):
        if time.time() - self.prev["learn_spell"] < min_wait_time:
            return
        if self.gs.player.can_learn:
            self.prev["learn_spell"] = time.time()
            await self.hd.press_and_release_key("ctrl+" + self.spell_list[self.level])
            self.level += 1

    async def goto_attach(self):
        print("goto_attach")
        start_time = time.time()
        await self.hd.press_key("f" + str(self.target))
        await self.hd.move_mouse(self.screen_center)
        await asyncio.sleep(0.1)
        await self.hd.press_and_release_key("w")

        inital_target = self.target
        while self.gs.player.is_dead == False and self.gs.champs[self.target-1].is_dead == False and self.enabled == True:
            if self.gs.player.attached == 1:
                return True
            if time.time() - start_time > 30:
                return False
            if inital_target != self.target:
                return False

            await asyncio.sleep(0.05)

    async def auto_heal(self, min_wait_time):
        if time.time() - self.prev["auto_heal"] < min_wait_time:
            return
        print("auto heal")
        if (self.gs.player.attached == 1 or self.gs.player.attached == 2) and\
                self.gs.player.is_dead == False and\
                self.gs.champs[self.target-1].is_dead == False and\
                self.gs.champs[self.target-1].hp_percent < 0.92:
            self.prev["auto_heal"] = time.time()

            await self.hd.press_and_release_key("e")

    async def retreat(self):
        print("retreat")
        while self.gs.player.is_dead == False and self.gs.champs[self.target-1].is_dead == True and self.enabled == True:
            await self.hd.press_and_release_key("e")
            await self.hd.move_mouse(self.gs.ally_base_loc)
            await self.hd.mouse_click()
            await asyncio.sleep(0.5)

    async def killmys(self):
        print("killmys")
        if self.gs.player.attached == 1:
            await self.hd.press_and_release_key("w")

        start_time = time.time()
        while self.gs.player.is_dead == False:
            if time.time() - start_time > 30:
                break
            await self.hd.move_mouse(self.screen_center)
            await asyncio.sleep(0.05)
            await self.hd.mouse_click()
            await asyncio.sleep(0.75)
            await self.hd.move_mouse(self.gs.enemy_base_loc)
            await asyncio.sleep(0.05)
            await self.hd.mouse_click(button="right")
            await asyncio.sleep(0.75)

    async def play_loop(self, fps):
        wait_time = 1/fps

        while True:
            if self.kms == True:
                await self.killmys()
                self.kms = False
            if self.enabled == True:
                if self.gs.player.is_dead == False:
                    if self.gs.champs[self.target-1].is_dead == False:
                        if self.gs.player.attached == 1 or self.gs.player.attached == 2:
                            await self.auto_heal(4)
                            await self.try_learn_spell(45)
                        else:
                            await self.goto_attach()

                    else:
                        await self.retreat()
            else:
                print("not enabled")

            await asyncio.sleep(wait_time)
