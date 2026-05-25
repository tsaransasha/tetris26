import random
from constants import COLS, ROWS, SHAPES, COLORS


def rotate_cw(cells):
    rotated = [(-c, r) for r, c in cells]
    min_r = min(r for r, _ in rotated)
    min_c = min(c for _, c in rotated)
    return [(r - min_r, c - min_c) for r, c in rotated]


def piece_cells(kind, rotation):
    c = list(SHAPES[kind])
    for _ in range(rotation % 4):
        c = rotate_cw(c)
    return c


class GameLogic:
    def __init__(self):
        self.board: list[list[str | None]] = [[None] * COLS for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.current: str | None = None
        self.rotation = 0
        self.cr = 0
        self.cc = 0

    def spawn(self) -> bool:
        self.current = random.choice(list(SHAPES.keys()))
        self.rotation = 0
        cells = piece_cells(self.current, self.rotation)
        w = max(c for _, c in cells) + 1
        self.cc = (COLS - w) // 2
        self.cr = 0
        if not self._fits(self.cr, self.cc, cells):
            self.game_over = True
            return False
        return True

    def _fits(self, br, bc, cells) -> bool:
        for dr, dc in cells:
            r, c = br + dr, bc + dc
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                return False
            if self.board[r][c] is not None:
                return False
        return True

    def try_move(self, dc: int, dr: int) -> bool:
        if self.game_over or not self.current:
            return False
        cells = piece_cells(self.current, self.rotation)
        if self._fits(self.cr + dr, self.cc + dc, cells):
            self.cr += dr
            self.cc += dc
            return True
        return False

    def try_rotate(self) -> bool:
        if self.game_over or not self.current or self.current == "O":
            return False
        new_r = (self.rotation + 1) % 4
        cells = piece_cells(self.current, new_r)
        for kr, kc in ((0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)):
            if self._fits(self.cr + kr, self.cc + kc, cells):
                self.rotation = new_r
                self.cr += kr
                self.cc += kc
                return True
        return False

    def hard_drop(self):
        if self.game_over or not self.current:
            return
        cells = piece_cells(self.current, self.rotation)
        while self._fits(self.cr + 1, self.cc, cells):
            self.cr += 1

    def lock_piece(self) -> int:
        if self.current is None:
            return 0
        cells = piece_cells(self.current, self.rotation)
        for dr, dc in cells:
            r, c = self.cr + dr, self.cc + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                self.board[r][c] = self.current
        cleared = self._clear_lines()
        if cleared:
            self.score += {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 800)
        return cleared

    def _clear_lines(self) -> int:
        kept = [row for row in self.board if not all(row)]
        cleared = ROWS - len(kept)
        while len(kept) < ROWS:
            kept.insert(0, [None] * COLS)
        self.board = kept
        return cleared

    def gravity_step(self) -> bool:
        if self.game_over or not self.current:
            return False
        cells = piece_cells(self.current, self.rotation)
        if self._fits(self.cr + 1, self.cc, cells):
            self.cr += 1
            return False
        self.lock_piece()
        return True

    def get_ghost_row(self) -> int:
        cells = piece_cells(self.current, self.rotation)
        ghost_r = self.cr
        while self._fits(ghost_r + 1, self.cc, cells):
            ghost_r += 1
        return ghost_r

    def reset(self):
        self.__init__()
