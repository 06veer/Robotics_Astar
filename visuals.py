"""Visualization helpers using pygame."""
import pygame
from typing import Tuple, List

from node import Node

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (200,200,200)
BLUE = (50,150,255)
GREEN = (50,200,50)
RED = (220,50,50)
ORANGE = (255,165,0)
PURPLE = (128,0,128)


def draw_grid(surface: pygame.Surface, grid_rows: int, grid_cols: int, cell_size: int):
    w,h = surface.get_size()
    for x in range(0, grid_cols*cell_size, cell_size):
        pygame.draw.line(surface, GREY, (x,0),(x,h))
    for y in range(0, grid_rows*cell_size, cell_size):
        pygame.draw.line(surface, GREY, (0,y),(w,y))


def draw_nodes(surface: pygame.Surface, grid, cell_size:int, open_set:list, closed_set:list, path:list):
    rows = len(grid)
    cols = len(grid[0])
    for r in range(rows):
        for c in range(cols):
            node = grid[r][c]
            rect = pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size)
            if node.is_obstacle:
                pygame.draw.rect(surface, BLACK, rect)

    for pos in closed_set:
        r,c = pos
        rect = pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size)
        pygame.draw.rect(surface, ORANGE, rect)

    for pos in open_set:
        r,c = pos
        rect = pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size)
        pygame.draw.rect(surface, BLUE, rect)

    for pos in path:
        r,c = pos
        rect = pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size)
        pygame.draw.rect(surface, PURPLE, rect)


def draw_start_end(surface: pygame.Surface, start: Node, end: Node, cell_size:int):
    if start:
        rect = pygame.Rect(start.col*cell_size, start.row*cell_size, cell_size, cell_size)
        pygame.draw.rect(surface, GREEN, rect)
    if end:
        rect = pygame.Rect(end.col*cell_size, end.row*cell_size, cell_size, cell_size)
        pygame.draw.rect(surface, RED, rect)


def draw_robot(surface: pygame.Surface, pos: Tuple[float,float], radius:int=8):
    pygame.draw.circle(surface, (0,0,0), (int(pos[0]), int(pos[1])), radius)
