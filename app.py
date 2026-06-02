import time
import tkinter as tk

from constants import STAR_BG
from logic import GameLogic
from screens import Screen, StartScreen, GameScreen


class TetrisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("✦ SPACE TETRIS ✦")
        self.root.configure(bg=STAR_BG)
        self.root.resizable(False, False)

        self._logic: GameLogic | None = None
        self._screen: Screen | None = None
        self._drop_after = None
        self._timer_after = None
        self._draw_after = None
        self._start_time = 0

        self._show_start()

    def _show_start(self):
        if self._drop_after:
            self.root.after_cancel(self._drop_after)
            self._drop_after = None
        if self._timer_after:
            self.root.after_cancel(self._timer_after)
            self._timer_after = None
        if self._screen:
            self._screen.destroy()
        self._screen = StartScreen(self.root, on_start=self._start_game)
        self._screen.build()

    def _start_game(self):
        if self._screen:
            self._screen.destroy()

        self._logic = GameLogic()
        game_screen = GameScreen(self.root, on_restart=self._restart_game, on_menu=self._show_start)
        game_screen.build()
        self._screen = game_screen

        self.root.bind_all("<Left>",  lambda e: self._logic.try_move(-1, 0))
        self.root.bind_all("<Right>", lambda e: self._logic.try_move(1, 0))
        self.root.bind_all("<Up>",    lambda e: self._logic.try_rotate())
        self.root.bind_all("<Down>",  lambda e: self._handle_drop())

        self._logic.spawn()
        self._start_time = time.time()
        self._schedule_drop()
        self._update_timer()
        self._draw_loop()

    def _restart_game(self):
        if self._drop_after:
            self.root.after_cancel(self._drop_after)
            self._drop_after = None
        if self._timer_after:
            self.root.after_cancel(self._timer_after)
            self._timer_after = None

        self._logic.reset()
        self._logic.spawn()
        self._start_time = time.time()
        self._screen.update_score(0)
        self._screen.update_level(1)
        self._screen.update_time(0)
        self._schedule_drop()
        self._update_timer()

    def _handle_drop(self):
        if not self._logic or self._logic.game_over:
            return
        self._logic.hard_drop()
        self._logic.lock_piece()
        self._logic.spawn()
        self._refresh_hud()
        self._schedule_drop()

    def _schedule_drop(self):
        if not self._logic or self._logic.game_over:
            return
        if self._drop_after:
            try:
                self.root.after_cancel(self._drop_after)
            except tk.TclError:
                pass
        self._drop_after = self.root.after(self._logic.drop_ms, self._gravity_tick)

    def _gravity_tick(self):
        self._drop_after = None
        if not self._logic or self._logic.game_over:
            return
        locked = self._logic.gravity_step()
        if locked:
            self._logic.spawn()
        self._refresh_hud()
        self._schedule_drop()

    def _refresh_hud(self):
        if not self._logic or not isinstance(self._screen, GameScreen):
            return
        self._screen.update_score(self._logic.score)
        self._screen.update_level(self._logic.level)

    def _update_timer(self):
        if not self._logic or self._logic.game_over:
            return
        elapsed = int(time.time() - self._start_time)
        self._screen.update_time(elapsed)
        self._timer_after = self.root.after(1000, self._update_timer)

    def _draw_loop(self):
        if self._logic and isinstance(self._screen, GameScreen):
            self._screen.draw(self._logic)
        self._draw_after = self.root.after(16, self._draw_loop)

    def run(self):
        self.root.mainloop()
