from PIL import ImageGrab, Image
import time
import numpy as np
import asyncio


class ScreenCapture():
    def __init__(self) -> None:
        self.count = 0
        self.start_time = time.time()
        self.screen_img: Image = None
        self.screen_array: np.array = None

    def update_screen(self, img=None):
        if img:
            self.screen_img = img
        else:
            self.screen_img = ImageGrab.grab()

        self.count += 1
        self.screen_array = np.asarray(self.screen_img)

    async def update_loop(self, fps: float):
        sleep_time = 1/fps
        while True:
            self.update_screen()
            await asyncio.sleep(sleep_time)
