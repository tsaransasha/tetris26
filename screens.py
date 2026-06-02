import random
import tkinter as tk
from constants import COLS, ROWS, CELL, COLORS, GLOW, STAR_BG
from logic import GameLogic, piece_cells
from starfield import StarField


class Screen:
    def __init__(self, root: tk.Tk):
        self.root = root

    def build(self):
        raise NotImplementedError

    def destroy(self):
        for w in self.root.winfo_children():
            w.destroy()


class StartScreen(Screen):
    def __init__(self, root: tk.Tk, on_start):
        super().__init__(root)
        self._on_start = on_start
        self._star_field: StarField | None = None

    def build(self):
        W, H = 320, 600
        self.root.configure(bg=STAR_BG)
        self.root.geometry(f"{W}x{H}")

        canvas = tk.Canvas(self.root, width=W, height=H, bg=STAR_BG, highlightthickness=0)
        canvas.place(x=0, y=0)

        self._draw_title()
        self._draw_launch_button()
        self._draw_hint()

        self._star_field = StarField(self.root, canvas, W, H)
        self._star_field.start()

    def _draw_title(self):
        frame = tk.Frame(self.root, bg=STAR_BG)
        frame.place(relx=0.5, rely=0.46, anchor="center")
        tk.Label(frame, text="✦  S P A C E  ✦", fg="#5599ff", bg=STAR_BG,
                 font=("Consolas", 11, "bold")).pack()
        tk.Label(frame, text="TETRIS", fg="#00e5ff", bg=STAR_BG,
                 font=("Consolas", 40, "bold")).pack()

    def _draw_launch_button(self):
        def _on_enter(e): btn.config(bg="#0055aa")
        def _on_leave(e): btn.config(bg="#003d80")

        btn = tk.Button(self.root, text="▶   LAUNCH", fg="#00e5ff", bg="#003d80",
                        font=("Consolas", 15, "bold"), width=12, relief="flat", bd=0,
                        activebackground="#0055aa", activeforeground="#ffffff",
                        cursor="hand2", command=self._on_start)
        btn.place(relx=0.5, rely=0.64, anchor="center")
        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)

    def _draw_hint(self):
        tk.Label(self.root,
                 text="← → переміщення   ↑ обертання   ↓ скинути",
                 fg="#2a4a6a", bg=STAR_BG, font=("Consolas", 8)
                 ).place(relx=0.5, rely=0.92, anchor="center")

    def destroy(self):
        if self._star_field:
            self._star_field.stop()
            self._star_field = None
        super().destroy()


class GameScreen(Screen):
    def __init__(self, root: tk.Tk, on_restart, on_menu):
        super().__init__(root)
        self._on_restart = on_restart
        self._on_menu = on_menu
        self.canvas: tk.Canvas | None = None
        self.lbl: tk.Label | None = None
        self.time_label: tk.Label | None = None
        self.level_label: tk.Label | None = None
        self.next_canvas: tk.Canvas | None = None
        self.game_stars: list[list[float]] = []
        self.canvas_w = COLS * CELL + 110
        self.canvas_h = ROWS * CELL + 4
        self.x0 = (self.canvas_w - COLS * CELL) // 2
        self.y0 = 2

    def build(self):
        self.root.configure(bg=COLORS["bg"])
        self.root.geometry("")

        top = tk.Frame(self.root, bg=COLORS["panel"], pady=4)
        top.pack(fill="x")

        score_frame = tk.Frame(top, bg=COLORS["panel"])
        score_frame.pack(side="left", padx=14)
        tk.Label(score_frame, text="SCORE", fg=COLORS["dim"], bg=COLORS["panel"],
                 font=("Consolas", 8, "bold")).pack(anchor="w")
        self.lbl = tk.Label(score_frame, text="0", fg=COLORS["accent"], bg=COLORS["panel"],
                            font=("Consolas", 18, "bold"))
        self.lbl.pack(anchor="w")

        time_frame = tk.Frame(top, bg=COLORS["panel"])
        time_frame.pack(side="left", padx=10)
        tk.Label(time_frame, text="TIME", fg=COLORS["dim"], bg=COLORS["panel"],
                 font=("Consolas", 8, "bold")).pack(anchor="w")
        self.time_label = tk.Label(time_frame, text="00:00", fg="#aaddff", bg=COLORS["panel"],
                                   font=("Consolas", 18, "bold"))
        self.time_label.pack(anchor="w")

        level_frame = tk.Frame(top, bg=COLORS["panel"])
        level_frame.pack(side="left", padx=10)
        tk.Label(level_frame, text="LEVEL", fg=COLORS["dim"], bg=COLORS["panel"],
                 font=("Consolas", 8, "bold")).pack(anchor="w")
        self.level_label = tk.Label(level_frame, text="1", fg="#ffe600", bg=COLORS["panel"],
                                    font=("Consolas", 18, "bold"))
        self.level_label.pack(anchor="w")

        next_frame = tk.Frame(top, bg=COLORS["panel"])
        next_frame.pack(side="right", padx=8)
        tk.Label(next_frame, text="NEXT", fg=COLORS["dim"], bg=COLORS["panel"],
                 font=("Consolas", 8, "bold")).pack()
        self.next_canvas = tk.Canvas(next_frame, width=76, height=54, bg=COLORS["bg"],
                                     highlightthickness=1, highlightbackground=COLORS["border"])
        self.next_canvas.pack()

        def _on_r_enter(e): restart_btn.config(bg="#003d80")
        def _on_r_leave(e): restart_btn.config(bg="#002860")

        restart_btn = tk.Button(top, text="⟳ RESTART", fg="#00e5ff", bg="#002860",
                                font=("Consolas", 9, "bold"), relief="flat", bd=0,
                                activebackground="#003d80", activeforeground="#ffffff",
                                cursor="hand2", command=self._on_restart)
        restart_btn.pack(side="right", padx=10, pady=6)
        restart_btn.bind("<Enter>", _on_r_enter)
        restart_btn.bind("<Leave>", _on_r_leave)

        tk.Frame(self.root, bg=COLORS["border"], height=1).pack(fill="x")

        self.canvas = tk.Canvas(self.root, width=self.canvas_w, height=self.canvas_h,
                                bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack(padx=6, pady=6)
        self.game_stars = self._make_game_stars(70)

    def _make_game_stars(self, count: int) -> list[list[float]]:
        stars = []
        for _ in range(count):
            if random.choice([True, False]):
                x = random.randint(4, max(5, self.x0 - 8))
            else:
                x = random.randint(self.x0 + COLS * CELL + 8, self.canvas_w - 4)
            stars.append([
                x,
                random.randint(0, self.canvas_h),
                random.uniform(0.7, 2.0),
                random.uniform(0.25, 1.1),
                random.randint(150, 255),
            ])
        return stars

    def _draw_game_stars(self):
        if not self.canvas:
            return
        field_left = self.x0
        field_right = self.x0 + COLS * CELL
        for star in self.game_stars:
            x, y, size, speed, bright = star
            c = int(bright)
            color = f"#{max(0, c - 70):02x}{max(0, c - 45):02x}{c:02x}"
            self.canvas.create_oval(x - size, y - size, x + size, y + size,
                                    fill=color, outline="")
            star[1] += speed
            if star[1] > self.canvas_h + size:
                if random.choice([True, False]):
                    star[0] = random.randint(4, max(5, field_left - 8))
                else:
                    star[0] = random.randint(field_right + 8, self.canvas_w - 4)
                star[1] = -size
                star[4] = random.randint(150, 255)

    def draw(self, logic: GameLogic):
        canvas = self.canvas
        canvas.delete("all")
        canvas.create_rectangle(0, 0, self.canvas_w, self.canvas_h, fill=COLORS["bg"], outline="")
        self._draw_game_stars()

        gw = COLS * CELL
        gh = ROWS * CELL
        x0, y0 = self.x0, self.y0

        canvas.create_rectangle(x0, y0, x0 + gw, y0 + gh,
                                 fill=COLORS["bg"], outline=COLORS["border"], width=2)

        for r in range(ROWS):
            for c in range(COLS):
                x = x0 + c * CELL
                y = y0 + r * CELL
                p = logic.board[r][c]
                if p:
                    self._draw_cell(x, y, p)
                else:
                    canvas.create_rectangle(x, y, x + CELL, y + CELL,
                                            outline=COLORS["grid"], width=1)

        if logic.current and not logic.game_over:
            cells = piece_cells(logic.current, logic.rotation)
            ghost_r = logic.get_ghost_row()

            if ghost_r != logic.cr:
                for dr, dc in cells:
                    rr, cc = ghost_r + dr, logic.cc + dc
                    if 0 <= rr < ROWS and 0 <= cc < COLS:
                        x = x0 + cc * CELL
                        y = y0 + rr * CELL
                        canvas.create_rectangle(x + 2, y + 2, x + CELL - 2, y + CELL - 2,
                                                fill="", outline=COLORS[logic.current], width=1)

            for dr, dc in cells:
                rr, cc = logic.cr + dr, logic.cc + dc
                if 0 <= rr < ROWS and 0 <= cc < COLS:
                    self._draw_cell(x0 + cc * CELL, y0 + rr * CELL, logic.current)

        self.update_level(logic.level)
        self._draw_next_piece(logic.next_piece)

        if logic.game_over:
            self._draw_game_over(x0, y0, gw, gh, logic.score)


    def _draw_next_piece(self, kind):
        if not self.next_canvas or not kind:
            return
        canvas = self.next_canvas
        canvas.delete("all")
        cells = piece_cells(kind, 0)
        preview_cell = 15
        min_r = min(r for r, _ in cells)
        max_r = max(r for r, _ in cells)
        min_c = min(c for _, c in cells)
        max_c = max(c for _, c in cells)
        piece_w = (max_c - min_c + 1) * preview_cell
        piece_h = (max_r - min_r + 1) * preview_cell
        x0 = (76 - piece_w) // 2
        y0 = (54 - piece_h) // 2

        for dr, dc in cells:
            x = x0 + (dc - min_c) * preview_cell
            y = y0 + (dr - min_r) * preview_cell
            canvas.create_rectangle(x, y, x + preview_cell, y + preview_cell,
                                    fill=GLOW.get(kind, "#111111"), outline="")
            canvas.create_rectangle(x + 2, y + 2, x + preview_cell - 2, y + preview_cell - 2,
                                    fill=COLORS[kind], outline="")

    def _draw_cell(self, x, y, kind):
        col = COLORS[kind]
        glow = GLOW.get(kind, "#111111")
        p = 2
        self.canvas.create_rectangle(x, y, x + CELL, y + CELL, fill=glow, outline="")
        self.canvas.create_rectangle(x + p, y + p, x + CELL - p, y + CELL - p,
                                     fill=col, outline="")
        h = col.lstrip("#")
        r2 = min(255, int(h[0:2], 16) + 70)
        g2 = min(255, int(h[2:4], 16) + 70)
        b2 = min(255, int(h[4:6], 16) + 70)
        light = f"#{r2:02x}{g2:02x}{b2:02x}"
        self.canvas.create_rectangle(x + p + 1, y + p + 1,
                                     x + CELL // 2, y + p + 4,
                                     fill=light, outline="")

    def _draw_game_over(self, x0, y0, gw, gh, score):
        canvas = self.canvas
        canvas.create_rectangle(x0, y0, x0 + gw, y0 + gh,
                                 fill="#000000", stipple="gray50")
        bx, by = x0 + gw // 2, y0 + gh // 2
        bw, bh = 210, 160

        canvas.create_rectangle(bx - bw // 2 - 3, by - bh // 2 - 3,
                                 bx + bw // 2 + 3, by + bh // 2 + 3,
                                 fill="#00e5ff", outline="")
        canvas.create_rectangle(bx - bw // 2, by - bh // 2,
                                 bx + bw // 2, by + bh // 2,
                                 fill="#060d17", outline="")
        canvas.create_text(bx, by - 44, text="✦  GAME OVER  ✦",
                           fill="#00e5ff", font=("Consolas", 14, "bold"))
        canvas.create_text(bx, by - 16, text=f"SCORE:  {score}",
                           fill="#ffffff", font=("Consolas", 12, "bold"))

        canvas.create_rectangle(bx - 85, by + 6, bx + 85, by + 34,
                                 fill="#003d80", outline="#00e5ff", width=1, tags="bg_restart")
        canvas.create_text(bx, by + 20, text="⟳   RESTART",
                           fill="#00e5ff", font=("Consolas", 11, "bold"), tags="btn_restart")

        canvas.create_rectangle(bx - 85, by + 44, bx + 85, by + 72,
                                 fill="#001830", outline="#5599ff", width=1, tags="bg_menu")
        canvas.create_text(bx, by + 58, text="⌂   ГОЛОВНЕ МЕНЮ",
                           fill="#5599ff", font=("Consolas", 11, "bold"), tags="btn_menu")

        for tag, fn in [("btn_restart", self._on_restart), ("bg_restart", self._on_restart),
                        ("btn_menu", self._on_menu), ("bg_menu", self._on_menu)]:
            canvas.tag_bind(tag, "<Button-1>", lambda e, f=fn: f())

        def _r_enter(e):
            canvas.itemconfig("btn_restart", fill="#ffffff")
            canvas.itemconfig("bg_restart", fill="#0055aa")
        def _r_leave(e):
            canvas.itemconfig("btn_restart", fill="#00e5ff")
            canvas.itemconfig("bg_restart", fill="#003d80")

        canvas.tag_bind("btn_restart", "<Enter>", _r_enter)
        canvas.tag_bind("btn_restart", "<Leave>", _r_leave)
        canvas.tag_bind("bg_restart", "<Enter>", _r_enter)
        canvas.tag_bind("bg_restart", "<Leave>", _r_leave)

        def _m_enter(e):
            canvas.itemconfig("btn_menu", fill="#ffffff")
            canvas.itemconfig("bg_menu", fill="#002a55")
        def _m_leave(e):
            canvas.itemconfig("btn_menu", fill="#5599ff")
            canvas.itemconfig("bg_menu", fill="#001830")

        canvas.tag_bind("btn_menu", "<Enter>", _m_enter)
        canvas.tag_bind("btn_menu", "<Leave>", _m_leave)
        canvas.tag_bind("bg_menu", "<Enter>", _m_enter)
        canvas.tag_bind("bg_menu", "<Leave>", _m_leave)

    def update_score(self, score: int):
        if self.lbl:
            self.lbl.config(text=str(score))

    def update_level(self, level: int):
        if self.level_label:
            self.level_label.config(text=str(level))

    def update_time(self, elapsed: int):
        if self.time_label:
            m, s = elapsed // 60, elapsed % 60
            self.time_label.config(text=f"{m:02}:{s:02}")