Step-by-step Code Explanation
----------------------------

1. `node.py` — defines `Node` that stores grid coordinates, obstacle state, A* costs (`g,h,f`), and a `parent` pointer used to reconstruct paths.
2. `grid.py` — builds a 2D matrix of `Node` objects and provides helper methods to access nodes and reset states.
3. `astar.py` — core A* implementation using a `heapq` priority queue. Uses Manhattan heuristic and supports 4-directional neighbors. Returns the path plus open/closed sets for visualization.
4. `isometric_visuals.py` — drawing utilities using Pygame to render the isometric scene, node states, start/end, robot, and obstacle types.
5. `main.py` — UI event loop: mouse controls for obstacles/start/end, orbit control by right-drag, keyboard controls for simulation, calls `astar` and animates the robot along the path while displaying metrics.

Run instructions: `python main.py` after installing `pygame`.
