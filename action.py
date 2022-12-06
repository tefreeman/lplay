from game_state import GameState
from typing import List
import time
import keyboard
import asyncio
from ainput import AInput
import mouse
import random


class Actions:
    def __init__(self, gs: GameState, hd: AInput, spell_list: List[str]) -> None:
        self.enabled = True
        self.block_mouse = False
        self.do_quick_attack = False
        self.kms = False
        self.screen_center = (955, 500)
        self.gs: GameState = gs
        self.spell_list: List[str] = spell_list
        self.target = 4
        self.hd: AInput = hd
        self.prev = {
            "learn_spell": 0,
            "auto_heal": 0
        }

    def toggle_quick_attack(self):
        self.do_quick_attack = True

    def set_target(self, tar: str):
        keyboard.release("f" + str(self.target))
        self.target = int(tar)
        keyboard.press_and_release("w")

    def toggle_kms(self):
        self.kms = not self.kms

    def toggle_enabled(self):
        self.enabled = not self.enabled
        self.kms = False
        print("done")

    def cast_self(self, key):
        self.block_mouse = True
        mouse.move(self.screen_center[0], self.screen_center[1])
        time.sleep(0.05)
        mouse.move(self.screen_center[0], self.screen_center[1])
        keyboard.press_and_release(key)
        time.sleep(0.05)
        keyboard.press_and_release(key)
        self.block_mouse = False

    async def try_learn_spell(self, min_wait_time):
        if time.time() - self.prev["learn_spell"] < min_wait_time:
            return
        if self.gs.player.can_learn:
            self.prev["learn_spell"] = time.time()

            for spell in self.spell_list:
                await self.hd.press_and_release_key("ctrl+" + spell)
                await asyncio.sleep(0.10)

    async def goto_attach(self):
        self.block_mouse = True
        print("goto_attach")
        await self.hd.press_key("f" + str(self.target))
        await self.hd.move_mouse(self.screen_center)
        await asyncio.sleep(0.15)
        await self.hd.press_and_release_key("w")

        await asyncio.sleep(0.35)
        await self.hd.release_key("f" + str(self.target))
        self.block_mouse = False

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
        self.block_mouse = True
        await self.hd.press_and_release_key("e")
        await self.hd.move_mouse(self.gs.ally_base_loc)
        await self.hd.mouse_click(button="right")
        await asyncio.sleep(0.1)
        self.block_mouse = False

    async def quick_attack(self):
        await self.hd.press_and_release_key("w")
        await asyncio.sleep(0.15)
        self.block_mouse = True
        await self.hd.mouse_click()
        await asyncio.sleep(0.15)
        await self.hd.press_key("f" + str(self.target))
        await self.hd.move_mouse(self.screen_center)
        await asyncio.sleep(0.15)
        await self.hd.press_and_release_key("w")
        await asyncio.sleep(0.15)
        await self.hd.release_key("f" + str(self.target))
        self.block_mouse = False

    async def killmys(self):
        self.block_mouse = True
        print("killmys")

        if self.gs.player.attached == 1 or self.gs.player.attached == 2:
            await self.hd.press_and_release_key("w")
            await asyncio.sleep(0.15)

        start_time = time.time()
        while time.time() - start_time < 30 and self.gs.player.is_dead == False and self.kms == True:
            target = (self.screen_center[0] + random.randint(-200, 200),
                      self.screen_center[1] + random.randint(-200, 200))
            sleep_time = random.random() + random.random() + 0.5
            await self.hd.move_mouse(self.screen_center)
            await self.hd.press_and_release_key("e")
            await asyncio.sleep(0.05)
            await self.hd.mouse_click()
            await asyncio.sleep(sleep_time)
            await self.hd.move_mouse(target)
            await asyncio.sleep(0.05)
            await self.hd.mouse_click(button="right")
        self.block_mouse = False

    async def buyItems(self):
        await self.hd.press_and_release_key("p")
        await asyncio.sleep(0.25)
        await self.hd.move_mouse((800, 220))
        await self.hd.mouse_click()
        await asyncio.sleep(0.25)

        items = [(390, 400), (440, 400), (385, 510), (440, 510),
                 (490, 510), (390, 620), (440, 620)]

        for item in items:
            await self.hd.move_mouse(item)
            await asyncio.sleep(0.1)
            await self.hd.double_click()
            await asyncio.sleep(0.1)

        await asyncio.sleep(0.1)
        await self.hd.press_and_release_key("p")

    async def play_loop(self, fps):
        wait_time = 1/fps

        # await self.buyItems()
        await asyncio.sleep(10)
        while True:
            if self.kms == True:
                await self.killmys()
                self.kms = False
            elif self.do_quick_attack == True:
                await self.quick_attack()
                self.do_quick_attack = False
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
                        asyncio.sleep(1.0)
                else:
                    # await self.buyItems()
                    asyncio.sleep(3.0)
            else:
                print("not enabled")

            await self.try_learn_spell(30)
            await asyncio.sleep(wait_time)
