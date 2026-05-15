Viva Questions and Answers
-------------------------

Q: Why A* over BFS?
A: A* uses a heuristic to guide search, often exploring far fewer nodes. BFS finds shortest path in unweighted graphs but explores uniformly.

Q: Why Manhattan distance?
A: Grid movement is restricted to 4 directions; Manhattan is admissible and consistent for this motion model.

Q: How can the grid be inspected from different sides?
A: Right-click and drag to orbit the 2.5D view around the scene center. This helps inspect obstacle placement and the start/goal positions more clearly.

Q: How is obstacle avoidance handled?
A: Obstacles are treated as impassable nodes. A* naturally avoids them when computing path.

Q: What is g, h, f?
A: g = cost so far, h = heuristic estimate to goal, f = g+h ranking metric.
