from screen_capture import ScreenCapture
from PIL import Image
import numpy as np
import colorsys


class Champ:
    c0 = (210, 779, 254, 784)
    offset = (-65, 779)

    hp_hsv_color_bounds = (75, 145, 20, 101, 0, 101)

    def hp_inbounds(hsv_pixel: tuple[3]) -> bool:
        if hsv_pixel[0] * 360 < Champ.hp_hsv_color_bounds[0] or\
                hsv_pixel[0] * 360 > Champ.hp_hsv_color_bounds[1]:
            return False
        if hsv_pixel[1] * 100 < Champ.hp_hsv_color_bounds[2] or\
                hsv_pixel[1] * 100 > Champ.hp_hsv_color_bounds[3]:
            return False
        if hsv_pixel[2] * 100 < Champ.hp_hsv_color_bounds[4] or\
                hsv_pixel[2] * 100 > Champ.hp_hsv_color_bounds[5]:
            return False
        return True

    def is_dead_bounds(hsv_pixel: tuple[3]) -> bool:
        if hsv_pixel[0] * 360 > 5 and\
                hsv_pixel[0] * 360 < 355:
            return False
        if hsv_pixel[1] * 100 < 30 or\
                hsv_pixel[1] * 100 > 60:
            return False
        if hsv_pixel[2] * 100 < 50:
            return False
        return True

    def __init__(self, num) -> None:
        start_x = Champ.c0[0] + Champ.offset[0] * num
        end_x = start_x + Champ.c0[2]-Champ.c0[0]
        self.hp_bar = (start_x, Champ.c0[1], end_x, Champ.c0[3])
        self.num = num
        self.hp_percent = 0.0
        self.mana_percent = 0.0
        self.is_dead = False

    def update(self, arr: np.array):
        self.update_is_dead(arr)

        if self.is_dead:
            return

        self.update_hp(arr)

    def update_is_dead(self, np_array):
        length = self.hp_bar[2] - self.hp_bar[0]
        count = 0
        for x in range(self.hp_bar[0], self.hp_bar[2]):
            r, g, b = np_array[self.hp_bar[1], x]
            if Champ.is_dead_bounds(colorsys.rgb_to_hls(r/255, g/255, b/255)) is True:
                count += 1

                if count > 2:
                    self.is_dead = True
                    self.hp_percent = 0.0
                    break

    def update_hp(self, np_array):
        length = self.hp_bar[2] - self.hp_bar[0]
        x = None
        for x in range(self.hp_bar[0], self.hp_bar[2]):
            r, g, b = np_array[self.hp_bar[1], x]
            if Champ.hp_inbounds(colorsys.rgb_to_hls(r/255, g/255, b/255)) is False:
                break

        self.hp_percent = (x - self.hp_bar[0]) / length

    def debug_print(self):
        print(self.num, self.hp_percent, self.mana_percent, self.is_dead)


class Player:
    hp_hsv_color_bounds = (75, 145, 20, 101, 0, 101)
    hp_bar_line = (753, 1054, 1060)
    mana_bar_line = (753, 1057, 1060)
    is_dead_line = (675, 1020, 715)
    signal_bar_line_brightness = 0.70
    level_up_line = (837, 923, 875, 923)

    def is_lvl_up_line(pixel: tuple[3]) -> bool:
        if pixel[0] * 360 > 54 and pixel[0] * 360 < 56 and pixel[2] > 0.85:
            return True
        else:
            return False

    def is_hp_signal_line(pixel: tuple[3]) -> bool:
        if pixel[1] > Player.signal_bar_line_brightness:
            return True
        return False

    def is_mana_signal_line(pixel: tuple[3]) -> bool:
        if pixel[1] > Player.signal_bar_line_brightness:
            return True
        return False

    def is_dead_signal_line(pixel: tuple[3]) -> bool:
        if pixel[0] < 0.01 and pixel[2] > 0.90:
            return True
        else:
            return False

    def __init__(self) -> None:
        self.hp = 0.0
        self.mana = 0.0
        self.is_dead = False
        self.can_learn = False
        self.attached = False

    def debug_print(self):
        print(self.hp, self.mana, self.is_dead, self.attached)

    def update(self, arr: np.array):
        self.update_is_dead(arr)

        if self.is_dead:
            return

        self.update_hp(arr)
        self.update_mana(arr)
        self.update_can_learn(arr)
        self.yuumi_is_attached(arr)

    def update_is_dead(self, np_array):
        count = 0
        x = None
        for x in range(self.is_dead_line[0], self.is_dead_line[2]):
            r, g, b = np_array[self.is_dead_line[1], x]
            if Player.is_dead_signal_line(colorsys.rgb_to_hls(r/255, g/255, b/255)) is True:
                count += 1

            if count > 1:
                self.is_dead = True
                break

    def update_hp(self, np_array):
        length = self.hp_bar_line[2] - self.hp_bar_line[0]
        x = None
        for x in range(self.hp_bar_line[0], self.hp_bar_line[2]):
            r, g, b = np_array[self.hp_bar_line[1], x]
            if Player.is_hp_signal_line(colorsys.rgb_to_hls(r/255, g/255, b/255)) is True:
                break

        self.hp = (x - self.hp_bar_line[0]) / length

    def update_mana(self, np_array):
        length = self.mana_bar_line[2] - self.mana_bar_line[0]
        x = None
        for x in range(self.mana_bar_line[0], self.mana_bar_line[2]):
            r, g, b = np_array[self.mana_bar_line[1], x]
            if Player.is_hp_signal_line(colorsys.rgb_to_hls(r/255, g/255, b/255)) is True:
                break

        self.mana = (x - self.mana_bar_line[0]) / length

    def update_can_learn(self, np_array):
        for x in range(self.level_up_line[0], self.level_up_line[2]):
            r, g, b = np_array[self.level_up_line[1], x]
            if Player.is_lvl_up_line(colorsys.rgb_to_hls(r/255, g/255, b/255)) is True:
                self.can_learn = True
                return

        self.can_learn = False

    def yuumi_is_attached(self, np_array):
        icon_spell_pt = (859, 1001)

        attached_color = (56, 79, 127)
        unattached_color = (65, 35, 151)

        if all(np_array[icon_spell_pt[1], icon_spell_pt[0]] == unattached_color):
            self.attached = 0

        elif all(np_array[icon_spell_pt[1], icon_spell_pt[0]] == attached_color):
            self.attached = 1

        else:
            self.attached = 2
