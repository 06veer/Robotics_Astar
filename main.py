"""Main application for the robot path planning simulator.

Controls:
- Left click: place/remove obstacle (random type: building, tree, car, person, animal)
- Press `S` while mouse over a cell: set start
- Press `F` while mouse over a cell: set finish/goal
- SPACE: run A*
- C: clear start/goal and search state only
- D: clear the entire map, including obstacles
- UP / DOWN: increase/decrease robot speed
- Right-drag: orbit view around the scene
- Two-finger scroll / mouse wheel: rotate view
- Ctrl + wheel: zoom in/out
- H: show/hide help panel

Note: simplified input to make the UI easier to use.
"""
import pygame
import sys
import time
import random
from typing import List, Tuple

from grid import Grid
from astar import astar
from isometric_visuals import IsoRenderer, draw_world, draw_robot

ROWS = 18
COLS = 26
WINDOW_SIZE = (1280, 840)
TILE_W = 46  # Zoomed in for better visibility
TILE_H = 23  # Zoomed in for better visibility


def draw_help_panel(surface: pygame.Surface, font: pygame.font.Font):
    """Draw a compact controls panel to keep the UI beginner-friendly."""
    panel_width = 320
    line_height = 20
    lines = [
        "Controls",
        "Left Click: Add Obstacle (random type)",
        "S: Set Start (hover cell)",
        "F: Set Finish (hover cell)",
        "SPACE: Run A*",
        "C: Clear Start/Goal",
        "D: Clear Entire Map",
        "UP/DOWN: Speed +/-",
        "Right-drag: Orbit View",
        "Wheel: Rotate View",
        "Ctrl+Wheel: Zoom In/Out",
        "H: Toggle this panel",
    ]
    panel_height = 10 + line_height * len(lines) + 6
    x = surface.get_width() - panel_width - 8
    y = 8

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 24, 34, 198))
    pygame.draw.rect(panel, (86, 146, 192, 210), panel.get_rect(), width=1, border_radius=12)
    surface.blit(panel, (x, y))

    for i, line in enumerate(lines):
        color = (255, 220, 120) if i == 0 else (236, 242, 248)
        txt = font.render(line, True, color)
        surface.blit(txt, (x + 10, y + 8 + i * line_height))


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Autonomous Robot Path Planning - A* Simulation")
    clock = pygame.time.Clock()

    renderer = IsoRenderer(
        tile_w=TILE_W,
        tile_h=TILE_H,
        origin_x=WINDOW_SIZE[0] // 2,
        origin_y=WINDOW_SIZE[1] // 2,
    )

    # Camera control
    camera_offset_x = 0
    camera_offset_y = 0
    view_angle_deg = 0.0
    camera_zoom = 1.0
    orbit_dragging = False
    orbit_velocity_deg_per_sec = 0.0
    mouse_down = False
    last_mouse_x = 0
    last_mouse_y = 0

    grid = Grid(ROWS, COLS)
    
    def seed_example_obstacles() -> None:
        # Puzzle-style starter layout with wider corridors and guaranteed access to both ends.
        safe_zones = set()
        for row in range(0, 4):
            for col in range(0, 4):
                safe_zones.add((row, col))
        for row in range(grid.rows - 4, grid.rows):
            for col in range(grid.cols - 4, grid.cols):
                safe_zones.add((row, col))

        corridor = set()
        for col in range(0, grid.cols):
            corridor.add((1, col))
            corridor.add((2, col))
        for row in range(2, grid.rows):
            corridor.add((row, grid.cols - 3))
        for col in range(3, grid.cols - 2):
            corridor.add((grid.rows - 3, col))
        for row in range(4, grid.rows - 3):
            corridor.add((row, 4))
            corridor.add((row, 5))
        for col in range(5, grid.cols - 6):
            corridor.add((5, col))
            corridor.add((6, col))
        for row in range(6, grid.rows - 5):
            corridor.add((row, grid.cols - 6))
            corridor.add((row, grid.cols - 7))

        wall_columns = [7, 11, 15, 19]
        wall_types = ["building", "tree", "car", "person"]

        for idx, col in enumerate(wall_columns):
            gap_rows = {2 + idx * 3, grid.rows - 4 - idx}
            for row in range(grid.rows):
                if (row, col) in corridor or (row, col) in safe_zones or row in gap_rows:
                    continue
                node = grid.grid[row][col]
                node.is_obstacle = True
                node.obstacle_type = wall_types[idx]

        wall_rows = [8, 12]
        row_types = ["animal", "building"]

        for idx, row in enumerate(wall_rows):
            gap_cols = {4 + idx * 5, grid.cols - 8 - idx * 2}
            for col in range(grid.cols):
                if (row, col) in corridor or (row, col) in safe_zones or col in gap_cols:
                    continue
                node = grid.grid[row][col]
                if node.is_obstacle:
                    continue
                node.is_obstacle = True
                node.obstacle_type = row_types[idx]

        accent_blocks = [
            (0, 6, "tree"),
            (3, 10, "car"),
            (5, 17, "person"),
            (9, 13, "animal"),
            (13, 7, "building"),
            (15, 21, "tree"),
        ]

        for row, col, obstacle_type in accent_blocks:
            if 0 <= row < grid.rows and 0 <= col < grid.cols:
                node = grid.grid[row][col]
                node.is_obstacle = True
                node.obstacle_type = obstacle_type

    seed_example_obstacles()

    running = True
    path: List[Tuple[int,int]] = []
    open_set = []
    closed_set = []
    path_cost = 0
    exec_time = 0
    animate = False
    robot_pos = None  # (row, col) in float grid coordinates
    speed = 8.0  # cells per second
    show_help = True
    path_unreachable = False  # Track if destination is blocked
    # animation state
    path_cells = []
    path_index = 0
    last_time = time.time()

    font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 21)

    while running:
        # Ensure renderer origin reflects current camera offset before handling input
        renderer.origin_x = WINDOW_SIZE[0] // 2 + camera_offset_x
        renderer.origin_y = WINDOW_SIZE[1] // 2 + camera_offset_y
        renderer.view_angle_deg = view_angle_deg
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if event.button == 3:  # Right click to pan (hold and drag)
                    orbit_dragging = True
                    last_mouse_x = x
                    last_mouse_y = y
                elif event.button == 1:  # Left click to place obstacles
                    picked = renderer.pixel_to_cell(x, y, ROWS, COLS)
                    if picked is not None:
                        # Prevent adding/removing obstacles while robot is moving or path is active
                        if animate or path_cells:
                            print("Cannot modify obstacles while robot is moving or path is active. Press C to clear.")
                        else:
                            # left click toggles obstacle with random type
                            r, c = picked
                            node = grid.grid[r][c]
                            node.is_obstacle = not node.is_obstacle
                            if node.is_obstacle:
                                # Randomly select obstacle type when placing
                                obstacle_types = ["building", "tree", "car", "person", "animal", "barrier", "crate"]
                                node.obstacle_type = random.choice(obstacle_types)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    orbit_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                # Orbit the camera when right mouse button is held
                if orbit_dragging:
                    x, y = event.pos
                    dx = x - last_mouse_x
                    dy = y - last_mouse_y
                    last_mouse_x = x
                    last_mouse_y = y
                    view_angle_deg = (view_angle_deg + dx * 0.45) % 360.0
                    orbit_velocity_deg_per_sec = dx * 18.0

            elif event.type == pygame.MOUSEWHEEL:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    camera_zoom = max(0.72, min(1.35, camera_zoom + event.y * 0.05))
                else:
                    # Touchpad two-finger scroll and wheel motion rotate the view by default.
                    view_angle_deg = (view_angle_deg + event.y * 6.0 + event.x * 6.0) % 360.0
                    orbit_velocity_deg_per_sec = (event.y + event.x) * 140.0

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # run A*
                    if grid.start and grid.end:
                        path, open_set, closed_set, path_cost, exec_time = astar(grid.grid, grid.start, grid.end)
                        if path:
                            animate = True
                            robot_pos = (float(grid.start.row), float(grid.start.col))
                            path_cells = path
                            path_index = 0
                            last_time = time.time()
                            path_unreachable = False
                            print(f"Path found! Cost: {path_cost}, Time: {exec_time:.4f}s")
                        else:
                            animate = False
                            path_unreachable = True
                            print("Destination unreachable! Obstacles block the path.")
                    else:
                        print("Set start and end nodes before running A*")

                elif event.key == pygame.K_c:
                    grid.clear_path_states()
                    grid.start = None
                    grid.end = None
                    path = []
                    open_set = []
                    closed_set = []
                    animate = False
                    path_cells = []
                    path_index = 0
                    robot_pos = None
                    path_unreachable = False

                elif event.key == pygame.K_d:
                    grid.reset()
                    path = []
                    open_set = []
                    closed_set = []
                    animate = False
                    path_cells = []
                    path_index = 0
                    robot_pos = None
                    path_unreachable = False

                elif event.key == pygame.K_UP:
                    speed += 1.0
                elif event.key == pygame.K_DOWN:
                    speed = max(1.0, speed-1.0)
                elif event.key == pygame.K_h:
                    show_help = not show_help

                elif event.key == pygame.K_s:
                    # set start at mouse position
                    mx, my = pygame.mouse.get_pos()
                    picked = renderer.pixel_to_cell(mx, my, ROWS, COLS)
                    if picked is not None:
                        r, c = picked
                        node = grid.grid[r][c]
                        if grid.start:
                            grid.start.is_obstacle = False
                        grid.start = node
                        node.is_obstacle = False

                elif event.key == pygame.K_f:
                    # set finish/goal at mouse position
                    mx, my = pygame.mouse.get_pos()
                    picked = renderer.pixel_to_cell(mx, my, ROWS, COLS)
                    if picked is not None:
                        r, c = picked
                        node = grid.grid[r][c]
                        if grid.end:
                            grid.end.is_obstacle = False
                        grid.end = node
                        node.is_obstacle = False

        # animation step: follow path node-to-node
        if animate and path_cells:
            now = time.time()
            dt = now - last_time
            last_time = now
            if path_index < len(path_cells)-1:
                tr, tc = path_cells[path_index + 1]
                cur_r, cur_c = robot_pos
                dr = tr - cur_r
                dc = tc - cur_c
                dist = (dr*dr + dc*dc) ** 0.5
                if dist < 1e-3:
                    # reached the target node
                    path_index += 1
                    robot_pos = (float(tr), float(tc))
                else:
                    step = speed * dt
                    if step >= dist:
                        robot_pos = (float(tr), float(tc))
                        path_index += 1
                    else:
                        nr = cur_r + dr / dist * step
                        nc = cur_c + dc / dist * step
                        robot_pos = (nr, nc)
            else:
                animate = False

        # Smooth inertial rotation after the drag ends.
        if not orbit_dragging and abs(orbit_velocity_deg_per_sec) > 0.01:
            dt_rotate = clock.get_time() / 1000.0
            view_angle_deg = (view_angle_deg + orbit_velocity_deg_per_sec * dt_rotate) % 360.0
            damping = 0.92 ** (dt_rotate * 60.0)
            orbit_velocity_deg_per_sec *= damping
        elif not orbit_dragging:
            orbit_velocity_deg_per_sec = 0.0

        # draw
        # Apply camera/orbit state to renderer
        renderer.origin_x = WINDOW_SIZE[0] // 2 + camera_offset_x
        renderer.origin_y = WINDOW_SIZE[1] // 2 + camera_offset_y
        renderer.zoom = camera_zoom
        renderer.view_angle_deg = view_angle_deg

        draw_world(screen, renderer, grid.grid, open_set, closed_set, path, grid.start, grid.end)
        if robot_pos:
            draw_robot(screen, renderer, robot_pos)

        # Title banner for a more professional presentation.
        banner = pygame.Surface((560, 72), pygame.SRCALPHA)
        banner.fill((16, 28, 42, 170))
        pygame.draw.rect(banner, (93, 148, 196, 210), banner.get_rect(), width=1, border_radius=14)
        title_font = pygame.font.SysFont(None, 30, bold=True)
        subtitle_font = pygame.font.SysFont(None, 20)
        banner.blit(title_font.render("Autonomous Robot Path Planning", True, (248, 251, 255)), (16, 10))
        banner.blit(subtitle_font.render("A* search • orbit camera • obstacle avoidance • interactive simulation", True, (206, 220, 232)), (16, 39))
        screen.blit(banner, (16, 14))

        # Draw orbit control hint
        hint_txt = small_font.render("Right-drag orbit | wheel/two-finger scroll rotate | Ctrl+wheel zoom", True, (74, 88, 102))
        screen.blit(hint_txt, (WINDOW_SIZE[0] - 600, WINDOW_SIZE[1] - 28))

        # HUD
        hud = pygame.Surface((360, 68), pygame.SRCALPHA)
        hud.fill((20, 28, 39, 190))
        pygame.draw.rect(hud, (116, 171, 214, 200), hud.get_rect(), width=1, border_radius=12)
        hud_lines = [
            f"Path cost: {path_cost if path_cost != float('inf') else 'N/A'}",
            f"Time: {exec_time:.4f}s   Speed: {speed:.1f} cell/s",
            f"Zoom: {camera_zoom:.2f}x   Orbit: {view_angle_deg:.0f} deg",
        ]
        for idx, text in enumerate(hud_lines):
            hud.blit(font.render(text, True, (240, 245, 250)), (14, 8 + idx * 19))
        screen.blit(hud, (16, WINDOW_SIZE[1] - 88))
        
        # Show unreachable message if destination is blocked
        if path_unreachable:
            unreachable_txt = font.render("Destination UNREACHABLE - Robot blocked by obstacles!", True, (220, 50, 50))
            screen.blit(unreachable_txt, (5, 30))
        
        if show_help:
            draw_help_panel(screen, small_font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
