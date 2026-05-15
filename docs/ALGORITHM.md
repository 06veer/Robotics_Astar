Algorithm Explanation
---------------------

This project uses the A* search algorithm to find the shortest path on a 4-connected grid and then visualizes that path in a 2.5D isometric simulator.

Project idea:
- The user places a start point, goal point, and obstacles.
- A* computes the best path while avoiding blocked cells.
- The simulator shows open set, closed set, final path, and animated robot movement.
- The orbiting camera lets the user inspect the scene from different angles.

Why A* is used:
- It finds optimal paths when the heuristic is admissible.
- It is faster than uninformed search in most practical grid path planning problems.
- It is easy to explain, implement, and visualize for an engineering project.

Cost functions:
- g(n): cost from start to node n (we use uniform cost = 1 per move)
- h(n): heuristic estimate to goal (Manhattan distance)
- f(n) = g(n) + h(n)

At each iteration, the node with lowest `f` in the open set is expanded. Neighbors are relaxed and pushed to a priority queue. The algorithm terminates when the goal is popped from the open set or the open set becomes empty.

Heuristic: Manhattan distance ensures admissibility for 4-directional movement.

Applications of this project:
- Mobile robot navigation in warehouses or labs.
- Classroom demonstrations of search algorithms and robotics basics.
- Game AI pathfinding on grid maps.
- Indoor delivery robots moving around static obstacles.
- Simulation of route planning before deploying real robots.

Demo obstacle setup:
- The project starts with a puzzle-style set of sample obstacles so the path is harder to find at first glance.
- `C` keeps the obstacle layout and only clears the start/goal nodes and path state.
- `D` clears the entire map, including all obstacles.

How to explain the project clearly:
- `main.py` handles user input, animation, and camera orbit.
- `grid.py` stores the grid and obstacle state.
- `node.py` stores each cell's cost and parent data.
- `astar.py` performs the search.
- `isometric_visuals.py` draws the scene and supports orbit-aware picking.

In simple words, the project is a visual robot path planner: you place obstacles, choose start and goal, run A*, and watch the robot move through the shortest available route.
