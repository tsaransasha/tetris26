✦ Space Tetris

A classic Tetris game implemented in Python using the built-in **tkinter** library. The project includes complete game logic, an animated starfield background, a landing-preview "ghost" piece, score tracking, and an in-game timer.

🌟 Key Features

* **Main Menu:** A start screen with an animated starfield background and a `LAUNCH` button.
* **Animated Starfield:** Stars of varying size, brightness, and speed fall continuously in the background, with each star recycled to the top once it leaves the screen.
* **Game Logic:**
    * Full implementation of the 7 classic Tetris shapes (I, O, T, S, Z, J, L).
    * Piece movement, rotation (with wall-kick), and instant "Hard Drop".
    * Collision detection with the walls, the floor, and other locked pieces.
    * Clearing completed lines and scoring points.
    * A "ghost" outline that shows where the current piece will land.
* **Interface and Rendering:**
    * Rendering of the game board, grid, and the falling piece with a neon, 3D-style cube look.
    * A top panel that displays the current score and the timer.
    * A "Game Over" screen showing the final score, with clickable buttons to restart or return to the menu.
* **Timer:** An in-game timer that tracks the total session time.

 🎮 How to Play

* **Piece Movement:**
    * `◄` (Left Arrow): Move the piece left.
    * `►` (Right Arrow): Move the piece right.
    * `▼` (Down Arrow): Hard drop — instantly drop and lock the piece.
* **Rotation:**
    * `▲` (Up Arrow): Rotate the piece clockwise.
* **Game Over Screen (mouse):**
    * Click **RESTART** to start a new game.
    * Click **MAIN MENU** to return to the start screen.

> Scoring: 100 / 300 / 500 / 800 points for clearing 1 / 2 / 3 / 4 lines at once.

## 🛠️ Installation and Setup

To run the game you only need Python — no external libraries are required.

**Requirements**

* Python 3.10 or newer (the code uses the `X | None` type-annotation syntax).
* `tkinter`, which ships with the standard Python distribution. On some Linux systems you may need to install it separately, e.g. `sudo apt install python3-tk`.

**Steps**

1. Clone the repository (replace the URL with your own):

```
git clone git@github.com:tsaransasha/tetris26.git
cd tetris26
```

2. No third-party dependencies are needed — `tkinter` is part of the standard library.

3. Run the game. The entry point is `main-2.py`:

```
python main-2.py
```

## 📁 Project Structure

| File | Responsibility |
|------|----------------|
| `constants.py` | Settings: board size, cell size, drop speed, piece shapes, and the color palette. |
| `logic.py`     | Game state and rules (`GameLogic`): the board, the current piece, movement, rotation, collisions, line clearing, and scoring. |
| `screens.py`   | User interface: the menu screen (`StartScreen`) and the game screen (`GameScreen`), plus board and piece rendering. |
| `starfield.py` | The animated starfield background (`StarField`). |
| `app.py`       | The main `TetrisApp` class: creates the window, switches screens, handles keyboard input, and runs the game loop. |
| `main-2.py`    | The entry point — launches the application (`TetrisApp().run()`). |

## 🧩 How It Works

The project separates concerns across three layers:

* **Logic (`logic.py`)** — the `GameLogic` class knows the rules but draws nothing.
* **Interface (`screens.py`)** — the screens only render the state provided by `GameLogic`.
* **Control (`app.py`)** — `TetrisApp` ties everything together: it shows the start screen, starts the game on `LAUNCH`, binds the keys, and schedules three repeating loops via `tkinter`'s `after()`:
    * the piece falls every `DROP_MS` milliseconds (`_gravity_tick`);
    * the timer updates once per second (`_update_timer`);
    * the board is redrawn roughly 60 times per second (`_draw_loop`).

Screens communicate with the controller through callbacks (`on_start`, `on_restart`, `on_menu`), and switching screens follows a simple "destroy the old one, build the new one" pattern.
