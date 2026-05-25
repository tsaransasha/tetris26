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

        self._draw_planet(canvas, W, H)
        self._draw_title()
        self._draw_launch_button()
        self._draw_hint()

        self._star_field = StarField(self.root, canvas, W, H)
        self._star_field.start()

    def _draw_planet(self, canvas: tk.Canvas, W: int, H: int):
        cx, cy, pr = W // 2, 165, 54
        canvas.create_oval(cx - pr - 12, cy - pr - 12, cx + pr + 12, cy + pr + 12,
                           fill="#001428", outline="#004488", width=2)
        for i, col in enumerate(["#0a2a50", "#0d3a6e", "#1055a0", "#1a6ec0", "#2288e0"]):
            off = i * 10
            canvas.create_oval(cx - pr + off // 2, cy - pr + off,
                                cx + pr - off // 2, cy + pr, fill=col, outline="")
        for rk, col, w in [(62, "#1a4a80", 3), (72, "#0d3060", 2), (80, "#082050", 1)]:
            canvas.create_oval(cx - rk, cy - rk // 4, cx + rk, cy + rk // 4,
                                outline=col, width=w)
        canvas.create_oval(cx - 20, cy - 22, cx + 4, cy - 4, fill="#4499cc", outline="")

    def _draw_title(self):
        frame = tk.Frame(self.root, bg=STAR_BG)
        frame.place(relx=0.5, rely=0.60, anchor="center")
        tk.Label(frame, text="✦  S P A C E  ✦", fg="#5599ff", bg=STAR_BG,
                 font=("Consolas", 11, "bold")).pack()
        tk.Label(frame, text="TETRIS", fg="#00e5ff", bg=STAR_BG,
                 font=("Consolas", 40, "bold")).pack()
        tk.Label(frame, text="─────────────", fg="#1a3a5c", bg=STAR_BG,
                 font=("Consolas", 12)).pack(pady=(0, 4))

    def _draw_launch_button(self):
        def _on_enter(e): btn.config(bg="#0055aa")
        def _on_leave(e): btn.config(bg="#003d80")

        btn = tk.Button(self.root, text="▶   LAUNCH", fg="#00e5ff", bg="#003d80",
                        font=("Consolas", 15, "bold"), width=12, relief="flat", bd=0,
                        activebackground="#0055aa", activeforeground="#ffffff",
                        cursor="hand2", command=self._on_start)
        btn.place(relx=0.5, rely=0.78, anchor="center")
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
        self.x0 = self.y0 = 2

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
        time_frame.pack(side="left", padx=14)
        tk.Label(time_frame, text="TIME", fg=COLORS["dim"], bg=COLORS["panel"],
                 font=("Consolas", 8, "bold")).pack(anchor="w")
        self.time_label = tk.Label(time_frame, text="00:00", fg="#aaddff", bg=COLORS["panel"],
                                   font=("Consolas", 18, "bold"))
        self.time_label.pack(anchor="w")

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

        gw = COLS * CELL + 4
        gh = ROWS * CELL + 4
        self.canvas = tk.Canvas(self.root, width=gw, height=gh,
                                bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack(padx=6, pady=6)

    def draw(self, logic: GameLogic):
        canvas = self.canvas
        canvas.delete("all")

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

        if logic.game_over:
            self._draw_game_over(x0, y0, gw, gh, logic.score)

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

    def update_time(self, elapsed: int):
        if self.time_label:
            m, s = elapsed // 60, elapsed % 60
            self.time_label.config(text=f"{m:02}:{s:02}")
