import random
import tkinter as tk
from constants import STAR_COUNT


class StarField:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas, w: int, h: int, count: int = STAR_COUNT):
        self._root = root
        self._canvas = canvas
        self._w = w
        self._h = h
        self._stars = self._make_stars(count)
        self._after_id = None

    def _make_stars(self, count: int) -> list:
        return [
            [
                random.randint(0, self._w),
                random.randint(0, self._h),
                random.uniform(0.6, 2.4),
                random.uniform(0.2, 1.4),
                random.randint(140, 255),
            ]
            for _ in range(count)
        ]

    def start(self):
        self._tick()

    def stop(self):
        if self._after_id:
            self._root.after_cancel(self._after_id)
            self._after_id = None

    def _tick(self):
        self._canvas.delete("all")
        for star in self._stars:
            x, y, size, speed, bright = star
            c = int(bright)
            r_ch = max(0, c - 40)
            color = f"#{r_ch:02x}{r_ch:02x}{c:02x}"
            self._canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=color, outline="",
            )
            star[1] += speed
            if star[1] > self._h + size:
                star[0] = random.randint(0, self._w)
                star[1] = -size
                star[4] = random.randint(140, 255)
        self._after_id = self._root.after(28, self._tick)
