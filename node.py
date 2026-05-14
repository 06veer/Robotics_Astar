"""Node representation for grid cells."""
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass(order=True)
class PriorityNode:
    priority: int
    node: any=field(compare=False)


class Node:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_obstacle = False
        self.obstacle_type: Optional[str] = None  # building, tree, car, person, animal
        self.g = float('inf')  # cost from start
        self.h = 0  # heuristic
        self.f = float('inf')  # total cost
        self.parent: Optional['Node'] = None

    def pos(self) -> Tuple[int,int]:
        return (self.row, self.col)

    def reset(self):
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None

    def __repr__(self):
        return f"Node({self.row},{self.col})"
