Report Content (concise)
------------------------

Introduction
- Problem statement and motivation for robot path planning.
- What the simulator does: place obstacles, choose start/goal, run A*, and inspect the path in an orbitable 2.5D view.

Methodology
- Grid-based modeling, A* algorithm, Manhattan heuristic, 2.5D isometric visualization with orbit control.

Applications
- Warehouse and lab robot navigation.
- Classroom demonstration of AI search and robotics.
- Game map pathfinding and obstacle avoidance.
- Pre-deployment simulation for mobile robots.

Demo behavior
- The simulator opens with a puzzle-style set of example obstacles so the scene is more challenging and better suited for explanation.
- `C` preserves the map and only resets the start/goal and search state.
- `D` clears the whole grid, removing all obstacles.

Implementation
- Describe files and important code snippets.
- `node.py` stores each cell state and path metadata.
- `grid.py` manages the grid and obstacle reset.
- `astar.py` calculates the optimal route.
- `isometric_visuals.py` renders the scene and obstacle types.
- `main.py` handles input, animation, and orbit controls.

Results
- Screenshots and observations: path cost, execution time, effect of obstacles, and visibility of the scene from multiple angles.

How the project works
- User places obstacles.
- User sets start and goal.
- A* searches the grid.
- The simulator animates the robot and shows the open/closed sets.
- The camera can orbit around the scene to inspect the result.

Conclusion
- Summary and future work.
