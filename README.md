# ✦ Space Tetris

A classic Tetris game developed in Python using the built-in tkinter library.  
The project implements complete Tetris gameplay, score tracking, level progression, a next-piece preview, a ghost piece, an in-game timer, and an animated space-style interface.

---

## Features

### Main Menu
- Animated falling snow/particle background.
- Centered TETRIS title.
- Clean interface without decorative arrows.
- LAUNCH button with smooth hover effects.

### Gameplay
- Classic Tetris mechanics.
- Random tetromino generation.
- Automatic line clearing.
- Score system.
- Level progression based on score.
- Increasing game speed at higher levels.
- Next-piece preview window.
- Ghost piece showing the landing position.
- Game Over screen.
- Pause functionality.

### Visual Effects
- Animated snow particles in the main menu.
- Animated snow particles in the empty side areas during gameplay.
- Space-inspired color palette.
- Smooth interface updates.

### Statistics
- Current score display.
- Current level display.
- Game timer.
- Lines cleared counter.

---

## Controls

| Key | Action |
|------|---------|
| ← | Move piece left |
| → | Move piece right |
| ↓ | Soft drop |
| ↑ | Rotate piece |
| Space | Hard drop |
| P | Pause / Resume |
| Esc | Exit game |

---

## Project Structure

tetris/
│
├── main.py          # Application entry point
├── app.py           # Main application initialization
├── logic.py         # Tetris game logic
├── screens.py       # Menu, game and game-over screens
├── constants.py     # Constants and configuration values
└── README.md
---

## Game Logic

The game is based on standard Tetris rules:

1. Random tetrominoes spawn at the top of the board.
2. The player moves and rotates pieces.
3. Completed rows are removed.
4. Points are awarded for cleared lines.
5. The level increases after reaching score thresholds.
6. Falling speed increases with each level.
7. The game ends when new pieces can no longer spawn.

---

## Technologies

- Python 3.x
- Tkinter

No external libraries are required.

## Installation

Clone the repository:

git clone <repository-url>
Open the project directory: 

cd tetris
Run the game:

py main-2.py
---
 Author

Created as a Python/Tkinter educational project demonstrating:
- Object-oriented programming
- GUI development
- Event handling
- Game loop implementation
- Collision detection
- State management
