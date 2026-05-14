"""Grid management for the simulation."""
from typing import List, Tuple, Optional
from node import Node


class Grid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Node]] = [[Node(r,c) for c in range(cols)] for r in range(rows)]
        self.start: Optional[Node] = None
        self.end: Optional[Node] = None

    def reset(self):
        for row in self.grid:
            for n in row:
                n.reset()
                n.is_obstacle = False
                n.obstacle_type = None
        self.start = None
        self.end = None

    def clear_path_states(self):
        for row in self.grid:
            for n in row:
                n.reset()

    def neighbors(self, node: Node) -> List[Node]:
        r, c = node.row, node.col
        res = []
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                res.append(self.grid[nr][nc])
        return res

    def node_at_pixel(self, x:int, y:int, cell_size:int) -> Node:
        c = x // cell_size
        r = y // cell_size
        return self.grid[r][c]
