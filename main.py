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
from visuals import draw_grid, draw_nodes, draw_start_end, draw_robot, WHITE

CELL_SIZE = 20
ROWS = 30
COLS = 40
WINDOW_SIZE = (COLS*CELL_SIZE, ROWS*CELL_SIZE)


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

    grid = Grid(ROWS, COLS)

    running = True
    path: List[Tuple[int,int]] = []
    open_set = []
    closed_set = []
    path_cost = 0
    exec_time = 0
    animate = False
    robot_pos = None
    speed = 200.0  # pixels per second
    show_help = True
    # animation state
    path_pixels = []
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
                node = grid.node_at_pixel(x,y,CELL_SIZE)
                if event.button == 1:
                    # left click toggles obstacle
                    node.is_obstacle = not node.is_obstacle

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # run A*
                    if grid.start and grid.end:
                        path, open_set, closed_set, path_cost, exec_time = astar(grid.grid, grid.start, grid.end)
                        if path:
                            animate = True
                            # robot pos at center of start cell
                            robot_pos = (grid.start.col*CELL_SIZE + CELL_SIZE/2, grid.start.row*CELL_SIZE + CELL_SIZE/2)
                            path_pixels = [(c*CELL_SIZE + CELL_SIZE/2, r*CELL_SIZE + CELL_SIZE/2) for r,c in path]
                            path_index = 0
                            last_time = time.time()
                        else:
                            animate = False
                    else:
                        print("Set start and end nodes before running A*")

                elif event.key == pygame.K_c:
                    grid.reset()
                    path = []
                    open_set = []
                    closed_set = []
                    animate = False
                    path_pixels = []
                    path_index = 0

                elif event.key == pygame.K_UP:
                    speed += 50
                elif event.key == pygame.K_DOWN:
                    speed = max(50, speed-50)
                elif event.key == pygame.K_h:
                    show_help = not show_help

                elif event.key == pygame.K_s:
                    # set start at mouse position
                    mx, my = pygame.mouse.get_pos()
                    node = grid.node_at_pixel(mx, my, CELL_SIZE)
                    if grid.start:
                        grid.start.is_obstacle = False
                    grid.start = node
                    node.is_obstacle = False

                elif event.key == pygame.K_f:
                    # set finish/goal at mouse position
                    mx, my = pygame.mouse.get_pos()
                    node = grid.node_at_pixel(mx, my, CELL_SIZE)
                    if grid.end:
                        grid.end.is_obstacle = False
                    grid.end = node
                    node.is_obstacle = False

        # animation step: follow path node-to-node
        if animate and path_pixels:
            now = time.time()
            dt = now - last_time
            last_time = now
            if path_index < len(path_pixels)-1:
                target = path_pixels[path_index+1]
                curx, cury = robot_pos
                tx, ty = target
                dx = tx - curx
                dy = ty - cury
                dist = (dx*dx + dy*dy)**0.5
                if dist < 1e-3:
                    # reached the target node
                    path_index += 1
                    robot_pos = (tx, ty)
                else:
                    step = speed * dt
                    if step >= dist:
                        robot_pos = (tx, ty)
                        path_index += 1
                    else:
                        nx = curx + dx / dist * step
                        ny = cury + dy / dist * step
                        robot_pos = (nx, ny)
            else:
                animate = False

        # draw
        screen.fill(WHITE)
        draw_nodes(screen, grid.grid, CELL_SIZE, open_set, closed_set, path)
        draw_grid(screen, ROWS, COLS, CELL_SIZE)
        draw_start_end(screen, grid.start, grid.end, CELL_SIZE)
        if robot_pos:
            draw_robot(screen, robot_pos, radius=max(4, CELL_SIZE//4))

        # HUD
        txt = font.render(f"Path cost: {path_cost if path_cost!=float('inf') else 'N/A'}  Time: {exec_time:.4f}s  Speed: {int(speed)} px/s", True, (0,0,0))
        screen.blit(txt, (5,5))
        if show_help:
            draw_help_panel(screen, small_font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
