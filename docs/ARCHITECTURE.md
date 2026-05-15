System Architecture
-------------------

- `node.py` — Node model storing costs, obstacle state, and parent pointer.
- `grid.py` — Grid container and utilities to access nodes.
- `astar.py` — Path planning algorithm using priority queue and Manhattan heuristic.
- `isometric_visuals.py` — 2.5D scene rendering, obstacle drawing, and orbit-aware picking.
- `main.py` — Application entrypoint, event loop, user interactions, orbit controls, and animation.

The system is modular to allow unit testing of `astar` and `grid` separately.

End-to-end flow:
- `main.py` receives user input and updates the simulator state.
- `astar.py` searches the grid when the user presses run.
- `isometric_visuals.py` draws the grid, obstacles, search states, and robot.
- The camera orbits the scene so the user can inspect object placement from multiple angles.
