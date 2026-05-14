# Autonomous Robot Path Planning and Obstacle Avoidance using A* Algorithm

This project is a Python-based simulation that demonstrates path planning and obstacle avoidance using the A* algorithm with a Pygame visualization.

The visualization now uses a 2.5D isometric view (instead of a flat grid) to provide a more professional robotics simulation look while keeping the same A* logic.

Run:

```bash
python main.py
```

Dependencies: `pygame`

Install with:

```bash
pip install pygame
```

Controls:
- Left click: place/remove obstacle
- Press `S` while mouse over a cell: set start node
- Press `F` while mouse over a cell: set destination/finish node
- SPACE: run A* and animate robot
- C: clear grid
- UP/DOWN: increase/decrease robot speed
- H: show/hide help panel

UI:
- A built-in help panel is shown on the top-right of the simulation window.

Visualization details:
- Isometric tile map rendering
- Raised 3D-style obstacle blocks
- Robot marker moving along the A* shortest path

