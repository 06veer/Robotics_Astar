# Autonomous Robot Path Planning and Obstacle Avoidance using A* Algorithm

This project is a Python-based simulation that demonstrates path planning and obstacle avoidance using the A* algorithm with a Pygame visualization.

The visualization uses a 2.5D isometric scene with orbit controls so you can inspect the grid, robot, start, goal, and obstacles from multiple viewing angles while keeping the same A* logic.

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
- C: clear start/goal and search state only
- D: clear the entire map, including all obstacles
- UP/DOWN: increase/decrease robot speed
- Right-drag: orbit the scene around the grid center
- H: show/hide help panel

UI:
- A built-in help panel is shown on the top-right of the simulation window.

Visualization details:
- Isometric tile map rendering with centered orbit camera
- Raised 3D-style obstacle blocks and a visible start/goal setup
- Robot marker moving along the A* shortest path
- Grid sized to fit the window while staying readable during rotation

Applications:
- Warehouse robot navigation and obstacle avoidance
- Classroom demonstrations of A* search and robotics
- Game AI pathfinding on grid maps
- Pre-deployment simulation for indoor mobile robots

Demo obstacles:
- The simulator starts with a puzzle-style maze layout made from staggered walls and gaps, so the initial path is harder to discover and better for demonstration.
- Press `C` to keep the obstacle map but reset the start and goal.
- Press `D` to remove every obstacle and start from a blank grid.

Suggested reading order:
- Start with `docs/ABSTRACT.md` for the project summary.
- Read `docs/OBJECTIVES.md` and `docs/ALGORITHM.md` to understand the goal and the A* logic.
- Use `docs/ARCHITECTURE.md` and `docs/CODE_WALKTHROUGH.md` to follow the modules and flow.
- Finish with `docs/REPORT.md` and `docs/VIVA_QA.md` for presentation and explanation support.

