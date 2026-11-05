# CPU-Maze (3D Raycasting on a Homemade CPU)

This is my second game project. It's a 3D maze game written in Python using the Kivy library.
The main feature: the rotation of the camera is calculated on my homemade 32-bit processor (emulated in Python)!

## How to Run
1. Install Python 3.
2. Install the Kivy library:
   pip install kivy
3. Run the main game:
   python main.py
4. Run the doors version:
   python doorsmain.py

## Controls
*   **FORWARD** - Move forward.
*   **<** - Turn left.
*   **>** - Turn right.
*   **USE** - Interact with doors (in doorsmain.py)

## Features
*   3D Raycasting engine (walls are rendered using math).
*   Mini-map in the top right corner.
*   Exit (green dot) - reach it to win (in main.py)!

## Alternative Versions
*   **Doors Mode (`doorsmain.py`):** A horror-inspired version. It features symmetric rooms connected by doors. You can open and close doors using the **USE** button. It also includes flickering lights and a jumpscare.

## Technical Notes & Performance
*   **FPS Limit:** The game is locked at 20 FPS. This is done intentionally to prevent overheating and lag on both mobile devices and older PCs. Do not try to increase it on low-end hardware.
*   **Performance:** This game uses a raycaster engine written in pure Python. On weak devices (old smartphones, budget laptops, or single-board computers), it may lag or run slowly. This is normal.
*   **If the game crashes:** Your device may not have enough CPU power to handle the 3D calculations. Try closing other apps or background processes.

## Technical Details
CPU: Written in Python from scratch. It calculates the camera rotation angle.
Kivy: Handles graphics and UI.

## Feedback
I am still learning, so I would appreciate any advice or bug reports!
