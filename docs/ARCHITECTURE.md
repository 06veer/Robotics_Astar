System Architecture
-------------------

- `node.py` — Node model storing costs and parent pointer.
- `grid.py` — Grid container and utilities to access nodes.
- `astar.py` — Path planning algorithm using priority queue and Manhattan heuristic.
- `visuals.py` — Pygame drawing helpers and color map.
- `main.py` — Application entrypoint, event loop, user interactions and animation.

The system is modular to allow unit testing of `astar` and `grid` separately.
