"""Main application for the robot path planning simulator.

Controls:
- Left click: place/remove obstacle
- Press `S` while mouse over a cell: set start
- Press `F` while mouse over a cell: set finish/goal
- SPACE: run A*
- C: clear grid
- UP / DOWN: increase/decrease robot speed
- H: show/hide help panel

Note: simplified input to make the UI easier to use.
"""
import pygame
import sys
import time
from typing import List, Tuple

from grid import Grid
from astar import astar
from isometric_visuals import IsoRenderer, draw_world, draw_robot

ROWS = 30
COLS = 40
WINDOW_SIZE = (1280, 840)
TILE_W = 28
TILE_H = 14


def draw_help_panel(surface: pygame.Surface, font: pygame.font.Font):
    """Draw a compact controls panel to keep the UI beginner-friendly."""
    panel_width = 290
    line_height = 20
    lines = [
        "Controls",
        "Left Click: Add/Remove Obstacle",
        "S: Set Start (hover cell)",
        "F: Set Finish (hover cell)",
        "SPACE: Run A*",
        "C: Clear Grid",
        "UP/DOWN: Speed +/-",
        "H: Toggle this panel",
    ]
    panel_height = 10 + line_height * len(lines) + 6
    x = surface.get_width() - panel_width - 8
    y = 8

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((20, 20, 20, 170))
    surface.blit(panel, (x, y))

    for i, line in enumerate(lines):
        color = (255, 235, 120) if i == 0 else (245, 245, 245)
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
        origin_y=80,
    )

    grid = Grid(ROWS, COLS)

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                picked = renderer.pixel_to_cell(x, y, ROWS, COLS)
                if event.button == 1 and picked is not None:
                    # left click toggles obstacle
                    r, c = picked
                    node = grid.grid[r][c]
                    node.is_obstacle = not node.is_obstacle

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

        # draw
        draw_world(screen, renderer, grid.grid, open_set, closed_set, path, grid.start, grid.end)
        if robot_pos:
            draw_robot(screen, renderer, robot_pos)

        # HUD
        txt = font.render(f"Path cost: {path_cost if path_cost!=float('inf') else 'N/A'}  Time: {exec_time:.4f}s  Speed: {speed:.1f} cell/s", True, (0,0,0))
        screen.blit(txt, (5,5))
        
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
