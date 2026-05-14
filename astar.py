"""A* pathfinding implementation."""
import time
from heapq import heappush, heappop
from typing import List, Tuple, Optional

from node import Node, PriorityNode


def manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


def reconstruct_path(end_node: Node) -> List[Tuple[int,int]]:
    path = []
    cur = end_node
    while cur:
        path.append(cur.pos())
        cur = cur.parent
    return path[::-1]


def astar(grid: List[List[Node]], start: Node, end: Node):
    """
    Run A* on a grid (4-directional). Returns (path, open_set_list, closed_set_list, path_cost, exec_time)
    """
    t0 = time.time()
    for row in grid:
        for n in row:
            n.reset()

    start.g = 0
    start.h = manhattan(start.pos(), end.pos())
    start.f = start.h

    open_heap = []
    heappush(open_heap, PriorityNode(start.f, start))
    open_set = {start.pos()}
    closed_set = set()

    rows = len(grid)
    cols = len(grid[0])

    while open_heap:
        current = heappop(open_heap).node
        open_set.discard(current.pos())

        if current.pos() == end.pos():
            path = reconstruct_path(current)
            exec_time = time.time() - t0
            return path, list(open_set), list(closed_set), current.g, exec_time

        closed_set.add(current.pos())

        neighbors = []
        r, c = current.row, current.col
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbors.append(grid[nr][nc])

        for nb in neighbors:
            if nb.is_obstacle or nb.pos() in closed_set:
                continue

            tentative_g = current.g + 1  # uniform cost for 4-directional grid
            if tentative_g < nb.g:
                nb.parent = current
                nb.g = tentative_g
                nb.h = manhattan(nb.pos(), end.pos())
                nb.f = nb.g + nb.h
                heappush(open_heap, PriorityNode(nb.f, nb))
                open_set.add(nb.pos())

    exec_time = time.time() - t0
    return [], list(open_set), list(closed_set), float('inf'), exec_time
