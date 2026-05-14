Algorithm Explanation
---------------------

We use the A* search algorithm to find the shortest path on a 4-connected grid.

Cost functions:
- g(n): cost from start to node n (we use uniform cost = 1 per move)
- h(n): heuristic estimate to goal (Manhattan distance)
- f(n) = g(n) + h(n)

At each iteration, the node with lowest `f` in the open set is expanded. Neighbors are relaxed and pushed to a priority queue. The algorithm terminates when the goal is popped from the open set or the open set becomes empty.

Heuristic: Manhattan distance ensures admissibility for 4-directional movement.
