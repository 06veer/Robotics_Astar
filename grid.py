"""Grid management for the simulation."""
import random
from typing import List, Tuple, Optional, Set
from node import Node


class Grid:
    DYNAMIC_OBSTACLE_TYPES = {"car", "person", "animal"}

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
                n.clear_obstacle_state()
        self.start = None
        self.end = None

    def clear_path_states(self):
        for row in self.grid:
            for n in row:
                n.reset()

    def set_obstacle(self, row: int, col: int, obstacle_type: Optional[str] = None) -> Node:
        node = self.grid[row][col]
        node.is_obstacle = True
        node.obstacle_type = obstacle_type
        node.is_dynamic = obstacle_type in self.DYNAMIC_OBSTACLE_TYPES
        if node.is_dynamic:
            if node.direction == (0, 0):
                node.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        else:
            node.direction = (0, 0)
        return node

    def clear_obstacle(self, row: int, col: int) -> Node:
        node = self.grid[row][col]
        node.clear_obstacle_state()
        node.reset()
        return node

    def _valid_destination(self, row: int, col: int, excluded_positions: Set[Tuple[int, int]], occupied_positions: Set[Tuple[int, int]]) -> bool:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        if (row, col) in excluded_positions:
            return False
        if (row, col) in occupied_positions:
            return False
        return True

    def update_dynamic_obstacles(self, excluded_positions: Optional[Set[Tuple[int, int]]] = None) -> bool:
        excluded_positions = set(excluded_positions or set())
        dynamic_nodes: List[Node] = []
        occupied_positions: Set[Tuple[int, int]] = set()

        for row in self.grid:
            for node in row:
                if node.is_obstacle:
                    occupied_positions.add(node.pos())
                if node.is_obstacle and node.is_dynamic:
                    dynamic_nodes.append(node)

        if not dynamic_nodes:
            return False

        random.shuffle(dynamic_nodes)
        moved = False
        reserved_destinations: Set[Tuple[int, int]] = set()

        for node in dynamic_nodes:
            source_pos = node.pos()

            candidate_directions = []
            if node.direction != (0, 0):
                candidate_directions.append(node.direction)
                candidate_directions.append((-node.direction[0], -node.direction[1]))
            candidate_directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])

            chosen_destination = None
            chosen_direction = node.direction
            for dr, dc in candidate_directions:
                if (dr, dc) == (0, 0):
                    continue
                dest_row = node.row + dr
                dest_col = node.col + dc
                destination = (dest_row, dest_col)
                if destination == source_pos:
                    continue
                if not self._valid_destination(dest_row, dest_col, excluded_positions, occupied_positions):
                    continue
                if destination in reserved_destinations:
                    continue
                chosen_destination = destination
                chosen_direction = (dr, dc)
                break

            if chosen_destination is None:
                continue

            dest_row, dest_col = chosen_destination
            dest_node = self.grid[dest_row][dest_col]

            dest_node.is_obstacle = True
            dest_node.obstacle_type = node.obstacle_type
            dest_node.is_dynamic = True
            dest_node.direction = chosen_direction
            dest_node.reset()

            node.clear_obstacle_state()
            node.reset()

            occupied_positions.add(chosen_destination)
            reserved_destinations.add(chosen_destination)
            moved = True

        return moved

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
