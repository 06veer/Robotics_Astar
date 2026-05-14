"""Isometric (2.5D) rendering helpers for the simulator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

from node import Node

# Scene palette
BACKGROUND = (235, 243, 248)
GRID_TILE = (210, 221, 230)
GRID_TILE_ALT = (201, 214, 224)
OUTLINE = (120, 136, 150)

OPEN_SET = (81, 156, 255)
CLOSED_SET = (255, 181, 76)
PATH_COLOR = (152, 95, 222)
START_COLOR = (76, 206, 120)
END_COLOR = (232, 76, 76)
OBSTACLE_TOP = (54, 62, 73)
OBSTACLE_LEFT = (38, 45, 56)
OBSTACLE_RIGHT = (29, 35, 45)
ROBOT_COLOR = (25, 25, 32)


def _clamp_color(c: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    return tuple(max(0, min(255, int(v * factor))) for v in c)


def _point_in_poly(px: float, py: float, poly: List[Tuple[float, float]]) -> bool:
    """Ray casting test for convex/concave polygons."""
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        intersects = ((yi > py) != (yj > py)) and (
            px < (xj - xi) * (py - yi) / ((yj - yi) + 1e-9) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


@dataclass
class IsoRenderer:
    tile_w: int
    tile_h: int
    origin_x: int
    origin_y: int
    block_h: int = 18

    def grid_to_screen(self, row: float, col: float) -> Tuple[float, float]:
        """Convert grid coordinates to top vertex of an isometric tile."""
        x = (col - row) * (self.tile_w / 2) + self.origin_x
        y = (col + row) * (self.tile_h / 2) + self.origin_y
        return x, y

    def tile_polygon(self, row: int, col: int, y_offset: float = 0.0) -> List[Tuple[float, float]]:
        x, y = self.grid_to_screen(row, col)
        y -= y_offset
        hw = self.tile_w / 2
        hh = self.tile_h / 2
        return [(x, y), (x + hw, y + hh), (x, y + self.tile_h), (x - hw, y + hh)]

    def robot_anchor(self, row: float, col: float) -> Tuple[float, float]:
        x, y = self.grid_to_screen(row, col)
        return x, y + self.tile_h * 0.55

    def pixel_to_cell(self, px: int, py: int, rows: int, cols: int) -> Optional[Tuple[int, int]]:
        """Map screen pixel to grid cell using inverse projection + polygon hit test."""
        cx = (px - self.origin_x) / (self.tile_w / 2)
        cy = (py - self.origin_y) / (self.tile_h / 2)

        row_f = (cy - cx) / 2
        col_f = (cy + cx) / 2

        base_r = int(round(row_f))
        base_c = int(round(col_f))

        # Try nearest candidates first for stable picking near tile boundaries.
        candidates = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r = base_r + dr
                c = base_c + dc
                if 0 <= r < rows and 0 <= c < cols:
                    candidates.append((r, c))

        candidates.sort(key=lambda rc: (rc[0] - row_f) ** 2 + (rc[1] - col_f) ** 2)

        for r, c in candidates:
            poly = self.tile_polygon(r, c)
            if _point_in_poly(px, py, poly):
                return r, c

        if 0 <= base_r < rows and 0 <= base_c < cols:
            return base_r, base_c
        return None


def _draw_tile(surface: pygame.Surface, poly: List[Tuple[float, float]], fill: Tuple[int, int, int]):
    pygame.draw.polygon(surface, fill, poly)
    pygame.draw.polygon(surface, OUTLINE, poly, width=1)


def _draw_block(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    """Draw a raised obstacle cube-like block."""
    top = renderer.tile_polygon(row, col, y_offset=renderer.block_h)
    base = renderer.tile_polygon(row, col, y_offset=0)

    # top corners: T, R, B, L
    t_top, r_top, b_top, l_top = top
    t_base, r_base, b_base, l_base = base

    left_face = [l_top, b_top, b_base, l_base]
    right_face = [b_top, r_top, r_base, b_base]

    pygame.draw.polygon(surface, OBSTACLE_LEFT, left_face)
    pygame.draw.polygon(surface, OBSTACLE_RIGHT, right_face)
    _draw_tile(surface, top, OBSTACLE_TOP)


def draw_world(
    surface: pygame.Surface,
    renderer: IsoRenderer,
    grid: List[List[Node]],
    open_set: List[Tuple[int, int]],
    closed_set: List[Tuple[int, int]],
    path: List[Tuple[int, int]],
    start: Optional[Node],
    end: Optional[Node],
):
    surface.fill(BACKGROUND)

    open_cells = set(open_set)
    closed_cells = set(closed_set)
    path_cells = set(path)

    rows = len(grid)
    cols = len(grid[0])

    # Back-to-front painter order for proper overlap.
    for diag in range(rows + cols - 1):
        for row in range(rows):
            col = diag - row
            if not (0 <= col < cols):
                continue
            node = grid[row][col]

            if (row + col) % 2 == 0:
                tile_color = GRID_TILE
            else:
                tile_color = GRID_TILE_ALT

            if (row, col) in closed_cells:
                tile_color = CLOSED_SET
            if (row, col) in open_cells:
                tile_color = OPEN_SET
            if (row, col) in path_cells:
                tile_color = PATH_COLOR
            if start and (row, col) == start.pos():
                tile_color = START_COLOR
            if end and (row, col) == end.pos():
                tile_color = END_COLOR

            tile_poly = renderer.tile_polygon(row, col)

            if node.is_obstacle:
                # Keep obstacle base subtle, then draw 3D block.
                _draw_tile(surface, tile_poly, _clamp_color(tile_color, 0.7))
                _draw_block(surface, renderer, row, col)
            else:
                _draw_tile(surface, tile_poly, tile_color)


def draw_robot(surface: pygame.Surface, renderer: IsoRenderer, robot_cell_pos: Tuple[float, float]):
    """Draw a detailed small autonomous robot with body, wheels, and antenna."""
    x, y = renderer.robot_anchor(robot_cell_pos[0], robot_cell_pos[1])
    
    # Scale robot based on tile size
    scale = renderer.tile_h / 14.0
    body_w = max(5, int(10 * scale))
    body_h = max(6, int(12 * scale))
    wheel_r = max(2, int(3 * scale))
    
    # Shadow beneath robot
    shadow_r = max(4, int(renderer.tile_h / 3))
    pygame.draw.ellipse(surface, (60, 65, 75, 100), (int(x - shadow_r), int(y + 2), int(shadow_r * 2), int(shadow_r * 0.7)))
    
    # Main robot body (dark chassis)
    body_rect = pygame.Rect(int(x - body_w // 2), int(y - body_h), body_w, body_h)
    pygame.draw.rect(surface, ROBOT_COLOR, body_rect, border_radius=2)
    pygame.draw.rect(surface, (100, 110, 130), body_rect, width=1, border_radius=2)
    
    # Left wheel
    left_wheel_x = int(x - body_w // 2 - 2)
    left_wheel_y = int(y - body_h // 2)
    pygame.draw.circle(surface, (50, 50, 60), (left_wheel_x, left_wheel_y), wheel_r)
    pygame.draw.circle(surface, (80, 85, 95), (left_wheel_x, left_wheel_y), wheel_r, width=1)
    
    # Right wheel
    right_wheel_x = int(x + body_w // 2 + 2)
    right_wheel_y = int(y - body_h // 2)
    pygame.draw.circle(surface, (50, 50, 60), (right_wheel_x, right_wheel_y), wheel_r)
    pygame.draw.circle(surface, (80, 85, 95), (right_wheel_x, right_wheel_y), wheel_r, width=1)
    
    # Small sensor/antenna on top (forward indicator)
    antenna_h = max(3, int(5 * scale))
    antenna_x = int(x)
    antenna_y_top = int(y - body_h - antenna_h)
    antenna_y_base = int(y - body_h)
    pygame.draw.line(surface, (200, 80, 80), (antenna_x, antenna_y_base), (antenna_x, antenna_y_top), width=1)
    pygame.draw.circle(surface, (220, 100, 100), (antenna_x, antenna_y_top), 1)
    
    # Front light indicator (small circle facing forward)
    light_y = int(y - body_h * 0.2)
    pygame.draw.circle(surface, (100, 200, 255), (int(x), light_y), max(1, wheel_r - 1))
