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
        await self.hd.press_key("f" + str(self.target))
        await self.hd.move_mouse(self.screen_center)
        await asyncio.sleep(0.1)
        await self.hd.press_and_release_key("w")

        await asyncio.sleep(0.1)

    async def auto_heal(self, min_wait_time):
        if time.time() - self.prev["auto_heal"] < min_wait_time:
            return
        if (self.gs.player.attached == 1 or self.gs.player.attached == 2) and\
                self.gs.player.is_dead == False and\
                self.gs.champs[self.target-1].is_dead == False and\
                self.gs.champs[self.target-1].hp_percent < 0.92:
            self.prev["auto_heal"] = time.time()
            await self.hd.press_and_release_key("e")
        elif self.gs.player.hp < 0.5 and self.gs.player.is_dead == False:
            self.prev["auto_heal"] = time.time()
            await self.hd.press_and_release_key("e")

    async def retreat(self):
        await self.hd.press_and_release_key("e")
        await self.hd.move_mouse(self.gs.ally_base_loc)
        await self.hd.mouse_click()

    async def killmys(self):
        print("killmys")

        if self.gs.player.attached == 1 or self.gs.player.attached == 2:
            await self.hd.press_and_release_key("w")

        await self.hd.move_mouse(self.screen_center)
        await asyncio.sleep(0.05)
        await self.hd.mouse_click()
        await asyncio.sleep(0.75)
        await self.hd.press_and_release_key("e")
        await self.hd.move_mouse(self.gs.enemy_base_loc)
        await asyncio.sleep(0.05)
        await self.hd.mouse_click(button="right")
        await asyncio.sleep(0.75)
        await self.hd.press_and_release_key("q")

    async def play_loop(self, fps):
        wait_time = 1/fps

        while True:
            if self.kms == True:
                await self.killmys()
                if self.gs.player.is_dead == True:
                    self.kms = False
            elif self.enabled == True:
                if self.gs.player.is_dead == False:
                    if self.gs.champs[self.target-1].is_dead == False:
                        if self.gs.player.attached == 1 or self.gs.player.attached == 2:
                            await self.auto_heal(2)
                        else:
                            await self.goto_attach()
                            asyncio.sleep(2.0)

                    else:
                        await self.retreat()
            else:
                print("not enabled")

            await self.try_learn_spell(30)
            await asyncio.sleep(wait_time)
