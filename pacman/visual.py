import pygame
from typing import Any
from mazegenerator.mazegenerator import MazeGenerator


def draw_maze(
        screen: pygame.Surface,
        maze: list[list[int]],
        cell_size: int,
        colors: dict[str, Any]) -> None:

    # def has_south_and_east_walls(x: int, y: int) -> bool:
    #     return ((maze[y][x] & 4) and (maze[y][x] & 2))

    # def has_south_and_west_walls(x: int, y: int) -> bool:
    #     return ((maze[y][x] & 4) and (maze[y][x] & 8))

    # def has_north_and_east_wall(x: int, y: int) -> bool:
    #     return ((maze[y][x] & 1) and (maze[y][x] & 2))

    # def has_north_and_west_wall(x: int, y: int) -> bool:
    #     return ((maze[y][x] & 1) and (maze[y][x] & 8))

    rows = len(maze)
    cols = len(maze[0])

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):

            # because pygame screen width is (len(maze[0]) * cell_size) + 50,
            # there are 25px left on each side of the maze
            offset_x = 25
            # a bit more space at the top to print scores etc
            offset_y = 100
            px = offset_x + x * cell_size
            py = offset_y + y * cell_size

            # top wall
            if cell & 1:
                pygame.draw.line(
                    screen,
                    colors["wall_blue"],
                    (px, py),
                    (px + cell_size, py), 5)

            # left wall
            if cell & 8:
                pygame.draw.line(
                    screen,
                    colors["wall_blue"],
                    (px, py),
                    (px, py + cell_size), 5)

            # right wall (last column)
            if x == (cols - 1) and (cell & 2):
                pygame.draw.line(
                    screen,
                    colors["wall_blue"],
                    (px + cell_size, py),
                    (px + cell_size, py + cell_size), 5)

            # bottom wall (last row)
            if y == rows - 1 and (cell & 4):
                pygame.draw.line(
                    screen,
                    colors["wall_blue"],
                    (px, py + cell_size),
                    (px + cell_size, py + cell_size), 5)

            # if x < cols - 1 and y < cols - 1:
            #     # if there's a part of the maze without walls
            #     if (not has_south_and_east_walls(x, y)
            #         and not has_south_and_west_walls(x + 1, y)
            #         and not has_north_and_east_wall(x, y + 1)
            #             and not has_north_and_west_wall(x + 1, y)):
            #         pygame.draw.line(
            #             screen, colors["wall_blue"],
            #             (px + cell_size, py + cell_size),
            #             (px + cell_size + 5, py + cell_size), 5)


def main_menu(screen: pygame.Surface, colors: dict[str, Any]) -> None:
    font = pygame.font.SysFont("arial", 48)
    small_font = pygame.font.SysFont("arial", 24)

    running = True

    while running:
        screen.fill(colors["black"])

        # create only an image with the text
        title_text = font.render("PAC-MAN", True, colors["yellow"])
        # "true" to have a not-pixelized text
        start_text = small_font.render("Press SPACE to start",
                                       True, colors["white"])
        quit_text = small_font.render("Press ESC to quit",
                                      True, colors["white"])

        # ".blit()" = put thoses images on screen
        screen.blit(
            title_text, (
                # to center the text image (x coord), 150 = y coord
                screen.get_width() // 2 - title_text.get_width() // 2, 150))
        screen.blit(
            start_text, (
                screen.get_width() // 2 - start_text.get_width() // 2, 300))
        screen.blit(
            quit_text, (
                screen.get_width() // 2 - quit_text.get_width() // 2, 350))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return


def init_game(level_1: MazeGenerator, cell_size: int) -> None:
    # 1,2,4,8 = north, east, south, west

    colors = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
        "wall_blue": (25, 25, 166),
        "ultramarine": (33, 33, 222),
        "peach": (222, 161, 133),
        "red": (253, 0, 0),
        "green": (0, 255, 0)
    }
    pygame.init()

    width = len(level_1.maze[0]) * cell_size + 50
    height = len(level_1.maze) * cell_size + 125

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pac-Man")

    main_menu(screen, colors)

    clock = pygame.time.Clock()  # create an intern timer for the game
    # to limit FPS
    running = True

    while running:
        # get all the events(mouse click, key press, close window etc)
        for event in pygame.event.get():
            # if event = close window
            if event.type == pygame.QUIT:
                running = False

        # cleaning screen at each frame
        screen.fill(colors["black"])

        # generating the drawing of the maze at each frame
        draw_maze(screen, level_1.maze, cell_size, colors)

        # displays it on the screen. "display" draws on a "hidden" zone,
        # and "flip" copy it to the real screen to make it visible
        pygame.display.flip()
        # max FPS for the game = 60FPS
        clock.tick(60)

    # cleanly close the windows and free window, memory
    # and graphical ressources
    pygame.quit()
