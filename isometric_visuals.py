"""Isometric (2.5D) rendering helpers for the simulator."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Optional, Tuple

import pygame

from node import Node

# Scene palette
BACKGROUND = (18, 25, 36)
GRID_TILE = (214, 225, 235)
GRID_TILE_ALT = (201, 214, 226)
OUTLINE = (110, 129, 146)

OPEN_SET = (81, 156, 255)
CLOSED_SET = (255, 181, 76)
PATH_COLOR = (0, 255, 150)  # Bright cyan/lime green
START_COLOR = (76, 206, 120)
END_COLOR = (232, 76, 76)
OBSTACLE_TOP = (54, 62, 73)
OBSTACLE_LEFT = (38, 45, 56)
OBSTACLE_RIGHT = (29, 35, 45)
ROBOT_COLOR = (25, 25, 32)
OBSTACLE_COLORS = {
    "building": ((122, 118, 104), (144, 139, 124), (167, 160, 146)),
    "tree": ((150, 95, 58), (42, 145, 48), (24, 112, 34)),
    "car": ((196, 53, 55), (231, 81, 88), (255, 209, 96)),
    "person": ((234, 204, 156), (58, 112, 196), (36, 40, 48)),
    "animal": ((184, 122, 76), (205, 145, 94), (36, 36, 36)),
    "barrier": ((205, 171, 64), (236, 232, 224), (62, 66, 78)),
    "crate": ((154, 108, 64), (184, 132, 79), (105, 77, 48)),
}


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
    zoom: float = 1.0
    view_angle_deg: float = 0.0
    focus_row: float = 0.0
    focus_col: float = 0.0

    @property
    def tile_w_px(self) -> float:
        return self.tile_w * self.zoom

    @property
    def tile_h_px(self) -> float:
        return self.tile_h * self.zoom

    @property
    def block_h_px(self) -> float:
        return self.block_h * self.zoom

    def _project_world_point(self, row: float, col: float, y_offset: float = 0.0) -> Tuple[float, float]:
        dx = col - self.focus_col
        dy = row - self.focus_row

        angle = math.radians(self.view_angle_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Rotate the world around the scene center before projecting it.
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a

        x = (rx - ry) * (self.tile_w_px / 2) + self.origin_x
        y = (rx + ry) * (self.tile_h_px / 2) + self.origin_y - y_offset * self.zoom
        return x, y

    def grid_to_screen(self, row: float, col: float) -> Tuple[float, float]:
        """Convert grid coordinates to top vertex of an isometric tile."""
        return self._project_world_point(row, col)

    def tile_polygon(self, row: int, col: int, y_offset: float = 0.0) -> List[Tuple[float, float]]:
        corners = [
            (row - 0.5, col - 0.5),
            (row - 0.5, col + 0.5),
            (row + 0.5, col + 0.5),
            (row + 0.5, col - 0.5),
        ]
        return [self._project_world_point(r, c, y_offset=y_offset) for r, c in corners]

    def robot_anchor(self, row: float, col: float) -> Tuple[float, float]:
        x, y = self._project_world_point(row, col)
        return x, y + self.tile_h_px * 0.55

    def pixel_to_cell(self, px: int, py: int, rows: int, cols: int) -> Optional[Tuple[int, int]]:
        """Map screen pixel to grid cell using inverse projection + polygon hit test."""
        dx = (px - self.origin_x) / (self.tile_w_px / 2)
        dy = (py - self.origin_y) / (self.tile_h_px / 2)

        rx = (dy + dx) / 2
        ry = (dy - dx) / 2

        angle = math.radians(self.view_angle_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        local_col = rx * cos_a + ry * sin_a
        local_row = -rx * sin_a + ry * cos_a

        row_f = local_row + self.focus_row
        col_f = local_col + self.focus_col

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

    top, right, bottom, left = poly
    highlight = _clamp_color(fill, 1.08)
    shadow = _clamp_color(fill, 0.82)
    pygame.draw.aaline(surface, highlight, top, right)
    pygame.draw.aaline(surface, highlight, top, left)
    pygame.draw.aaline(surface, shadow, right, bottom)
    pygame.draw.aaline(surface, shadow, left, bottom)


def _draw_drop_shadow(surface: pygame.Surface, poly: List[Tuple[float, float]], offset_x: int = 4, offset_y: int = 6):
    shadow_poly = [(x + offset_x, y + offset_y) for x, y in poly]
    pygame.draw.polygon(surface, (48, 57, 68), shadow_poly)


def _draw_background(surface: pygame.Surface):
    width, height = surface.get_size()
    bands = [
        (21, 30, 44),
        (24, 34, 50),
        (27, 38, 56),
        (30, 42, 61),
        (34, 47, 67),
        (38, 52, 73),
    ]
    band_height = max(1, height // len(bands))
    for index, color in enumerate(bands):
        pygame.draw.rect(surface, color, (0, index * band_height, width, band_height + 1))

    # Soft central spotlight so the grid stands out from the background.
    vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(vignette, (76, 119, 165, 38), (width * 0.17, height * 0.14, width * 0.66, height * 0.66))
    pygame.draw.ellipse(vignette, (255, 255, 255, 16), (width * 0.30, height * 0.24, width * 0.40, height * 0.40))
    surface.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _scene_sort_key(renderer: IsoRenderer, row: int, col: int) -> Tuple[float, float]:
    x, y = renderer.grid_to_screen(row, col)
    return (y, x)


def _draw_block(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    """Draw a raised obstacle cube-like block."""
    top = renderer.tile_polygon(row, col, y_offset=renderer.block_h_px)
    base = renderer.tile_polygon(row, col, y_offset=0)

    # top corners: T, R, B, L
    t_top, r_top, b_top, l_top = top
    t_base, r_base, b_base, l_base = base

    left_face = [l_top, b_top, b_base, l_base]
    right_face = [b_top, r_top, r_base, b_base]

    _draw_drop_shadow(surface, base, offset_x=5, offset_y=7)
    pygame.draw.polygon(surface, (72, 82, 96), left_face)
    pygame.draw.polygon(surface, (58, 67, 79), right_face)
    _draw_tile(surface, top, (97, 107, 121))


def _draw_building(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    """Draw a tall building with multiple levels."""
    scale = renderer.tile_h_px / 14.0
    block_h = int(30 * scale)  # Taller than normal blocks
    top = renderer.tile_polygon(row, col, y_offset=block_h)
    base = renderer.tile_polygon(row, col, y_offset=0)
    
    t_top, r_top, b_top, l_top = top
    t_base, r_base, b_base, l_base = base
    left_face = [l_top, b_top, b_base, l_base]
    right_face = [b_top, r_top, r_base, b_base]
    
    _draw_drop_shadow(surface, base, offset_x=6, offset_y=8)
    left_color, right_color, top_color = OBSTACLE_COLORS["building"]
    pygame.draw.polygon(surface, left_color, left_face)
    pygame.draw.polygon(surface, right_color, right_face)
    _draw_tile(surface, top, top_color)
    
    # Windows on top (small squares)
    x, y = renderer.grid_to_screen(row, col)
    y -= block_h
    win_size = max(2, int(3 * scale))
    for wx in range(-4, 5, 3):
        window = pygame.Rect(int(x + wx * 2), int(y + 4), win_size, win_size)
        pygame.draw.rect(surface, (45, 89, 152), window)
        pygame.draw.rect(surface, (120, 184, 255), window, width=1)


def _draw_tree(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    """Draw a tree with trunk and foliage."""
    scale = renderer.tile_h_px / 14.0
    x, y = renderer.grid_to_screen(row, col)
    
    # Trunk (brown rectangle)
    trunk_w = max(2, int(4 * scale))
    trunk_h = max(8, int(15 * scale))
    pygame.draw.ellipse(surface, (70, 80, 90), (int(x - trunk_w + 5), int(y - trunk_h + 10), int(trunk_w * 2), int(trunk_h * 0.55)))
    pygame.draw.rect(surface, (139, 90, 50), (int(x - trunk_w), int(y - trunk_h), int(trunk_w * 2), trunk_h), border_radius=1)
    
    # Foliage (green triangle/cone)
    foliage_top = int(y - trunk_h - int(12 * scale))
    foliage_r = max(6, int(10 * scale))
    left_color, mid_color, dark_color = OBSTACLE_COLORS["tree"]
    pygame.draw.circle(surface, (62, 72, 82), (int(x + 2), int(y - trunk_h + 10)), max(4, int(foliage_r * 0.55)))
    points = [
        (int(x), foliage_top),  # top
        (int(x + foliage_r), int(y - trunk_h + int(6 * scale))),  # right
        (int(x - foliage_r), int(y - trunk_h + int(6 * scale))),  # left
    ]
    pygame.draw.polygon(surface, mid_color, points)
    inner_points = [
        (int(x), int(foliage_top + foliage_r * 0.55)),
        (int(x + foliage_r * 0.6), int(y - trunk_h + int(4 * scale))),
        (int(x - foliage_r * 0.6), int(y - trunk_h + int(4 * scale))),
    ]
    pygame.draw.polygon(surface, left_color, inner_points)
    pygame.draw.polygon(surface, dark_color, points, width=1)


def _draw_car(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    """Draw a small car/vehicle."""
    scale = renderer.tile_h_px / 14.0
    x, y = renderer.grid_to_screen(row, col)
    
    car_w = max(8, int(12 * scale))
    car_h = max(5, int(8 * scale))
    
    pygame.draw.ellipse(surface, (70, 80, 90), (int(x - car_w // 2 + 5), int(y - car_h + 7), car_w, max(4, int(car_h * 0.55))))
    body_color, highlight_color, accent_color = OBSTACLE_COLORS["car"]
    # Car body (red)
    pygame.draw.rect(surface, body_color, (int(x - car_w // 2), int(y - car_h), car_w, car_h), border_radius=2)
    pygame.draw.rect(surface, highlight_color, (int(x - car_w // 2 + 1), int(y - car_h + 1), car_w - 2, max(2, car_h // 3)), border_radius=1)
    
    # Windows (light blue)
    window_w = max(2, int(3 * scale))
    pygame.draw.rect(surface, (100, 180, 220), (int(x - car_w // 3), int(y - car_h + 1), window_w, window_w))
    pygame.draw.rect(surface, (100, 180, 220), (int(x + car_w // 3 - window_w), int(y - car_h + 1), window_w, window_w))
    
    # Wheels (dark circles)
    wheel_r = max(2, int(2.5 * scale))
    pygame.draw.circle(surface, (30, 30, 30), (int(x - car_w // 3), int(y)), wheel_r)
    pygame.draw.circle(surface, (30, 30, 30), (int(x + car_w // 3), int(y)), wheel_r)
    pygame.draw.circle(surface, accent_color, (int(x), int(y - car_h + 2)), 1)


def _draw_person(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    """Draw a simple person figure."""
    scale = renderer.tile_h_px / 14.0
    x, y = renderer.grid_to_screen(row, col)
    
    head_r = max(2, int(3 * scale))
    body_h = max(4, int(6 * scale))
    
    pygame.draw.ellipse(surface, (70, 80, 90), (int(x - 4), int(y - body_h + 8), 8, max(5, int(body_h * 0.7))))
    body_color = OBSTACLE_COLORS["person"][1]
    # Head (yellow/skin)
    pygame.draw.circle(surface, (230, 200, 150), (int(x), int(y - body_h - head_r)), head_r)
    
    # Body (shirt - blue)
    pygame.draw.line(surface, body_color, (int(x), int(y - body_h)), (int(x), int(y)), width=max(1, int(2 * scale)))
    pygame.draw.circle(surface, (255, 240, 220), (int(x), int(y - body_h - head_r)), max(1, head_r - 1))
    
    # Arms
    arm_len = max(3, int(4 * scale))
    pygame.draw.line(surface, (230, 200, 150), (int(x - arm_len), int(y - body_h + 2)), (int(x + arm_len), int(y - body_h + 2)), width=1)
    
    # Legs (dark)
    leg_len = max(2, int(3 * scale))
    pygame.draw.line(surface, (50, 50, 50), (int(x - 1), int(y)), (int(x - 1), int(y + leg_len)), width=1)
    pygame.draw.line(surface, (50, 50, 50), (int(x + 1), int(y)), (int(x + 1), int(y + leg_len)), width=1)


def _draw_animal(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    """Draw a simple animal (dog-like)."""
    scale = renderer.tile_h_px / 14.0
    x, y = renderer.grid_to_screen(row, col)
    
    body_w = max(6, int(8 * scale))
    body_h = max(4, int(5 * scale))
    
    pygame.draw.ellipse(surface, (70, 80, 90), (int(x - body_w // 2 + 5), int(y - body_h + 7), body_w, max(4, int(body_h * 0.55))))
    base_color, highlight_color, dark_color = OBSTACLE_COLORS["animal"]
    # Body (brown)
    pygame.draw.ellipse(surface, base_color, (int(x - body_w // 2), int(y - body_h), body_w, body_h))
    pygame.draw.ellipse(surface, highlight_color, (int(x - body_w // 2 + 1), int(y - body_h + 1), max(2, body_w - 3), max(2, body_h // 2)))
    
    # Head (slightly larger circle)
    head_r = max(3, int(4 * scale))
    pygame.draw.circle(surface, highlight_color, (int(x + body_w // 3), int(y - body_h - 1)), head_r)
    pygame.draw.circle(surface, dark_color, (int(x + body_w // 3), int(y - body_h - 1)), head_r, width=1)
    
    # Eyes (black dots)
    eye_r = max(1, int(1.5 * scale))
    pygame.draw.circle(surface, (20, 20, 20), (int(x + body_w // 3 - 1), int(y - body_h - 2)), eye_r)
    pygame.draw.circle(surface, (20, 20, 20), (int(x + body_w // 3 + 1), int(y - body_h - 2)), eye_r)
    
    # Tail (curved line)
    pygame.draw.line(surface, dark_color, (int(x - body_w // 3), int(y - body_h // 2)), (int(x - body_w // 2 - 2), int(y - body_h // 2 - 2)), width=1)


def _draw_barrier(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    scale = renderer.tile_h_px / 14.0
    x, y = renderer.grid_to_screen(row, col)
    width = max(10, int(16 * scale))
    height = max(4, int(6 * scale))
    base_poly = [
        (int(x - width // 2), int(y - height)),
        (int(x + width // 2), int(y - height // 2)),
        (int(x), int(y + height // 2)),
        (int(x - width), int(y)),
    ]
    _draw_drop_shadow(surface, base_poly, 4, 7)
    pygame.draw.polygon(surface, OBSTACLE_COLORS["barrier"][0], base_poly)
    pygame.draw.line(surface, OBSTACLE_COLORS["barrier"][1], (int(x - width // 2), int(y - height)), (int(x + width // 2), int(y - height // 2)), width=2)
    pygame.draw.line(surface, OBSTACLE_COLORS["barrier"][2], (int(x - width), int(y)), (int(x), int(y + height // 2)), width=1)


def _draw_crate(surface: pygame.Surface, renderer: IsoRenderer, row: int, col: int):
    scale = renderer.tile_h_px / 14.0
    x, y = renderer.grid_to_screen(row, col)
    size = max(8, int(11 * scale))
    top = [(int(x), int(y - size)), (int(x + size), int(y - size // 2)), (int(x), int(y)), (int(x - size), int(y - size // 2))]
    shadow = [(px + 5, py + 7) for px, py in top]
    pygame.draw.polygon(surface, (60, 70, 80), shadow)
    pygame.draw.polygon(surface, OBSTACLE_COLORS["crate"][0], top)
    pygame.draw.polygon(surface, OBSTACLE_COLORS["crate"][1], top, width=1)
    pygame.draw.line(surface, OBSTACLE_COLORS["crate"][2], top[0], top[2], width=1)
    pygame.draw.line(surface, OBSTACLE_COLORS["crate"][2], top[1], top[3], width=1)


OBSTACLE_DRAWERS = {
    "building": _draw_building,
    "tree": _draw_tree,
    "car": _draw_car,
    "person": _draw_person,
    "animal": _draw_animal,
    "barrier": _draw_barrier,
    "crate": _draw_crate,
}


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
    _draw_background(surface)

    renderer.focus_row = (len(grid) - 1) / 2.0
    renderer.focus_col = (len(grid[0]) - 1) / 2.0

    open_cells = set(open_set)
    closed_cells = set(closed_set)
    path_cells = set(path)

    rows = len(grid)
    cols = len(grid[0])

    cells = [(row, col) for row in range(rows) for col in range(cols)]
    cells.sort(key=lambda rc: _scene_sort_key(renderer, rc[0], rc[1]))

    for row, col in cells:
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
                # Keep obstacle base subtle, then draw obstacle based on type.
                _draw_tile(surface, tile_poly, _clamp_color(tile_color, 0.78))
                
                # Draw obstacle based on its type
                obstacle_type = node.obstacle_type or "building"  # default to building
                if obstacle_type in OBSTACLE_DRAWERS:
                    OBSTACLE_DRAWERS[obstacle_type](surface, renderer, row, col)
                else:
                    _draw_block(surface, renderer, row, col)  # fallback
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
