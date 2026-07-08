from collections import deque
from collections.abc import Iterator


Coord = tuple[int, int]


def _get_neighbors(
    maze: list[list[int]], x: int, y: int
) -> Iterator[Coord]:
    """
    Yield reachable neighboring cells from a maze bitmask cell.

    Args:
        maze: the game maze, a list of walls.
        x: the x position of the current cell.
        y: the y position of the current cell.

    Returns:
        A coordinate iterator.
    """
    rows = len(maze)
    cols = len(maze[0])
    cell = maze[y][x]

    if not (cell & 1) and y > 0:
        yield (x, y - 1)
    if not (cell & 2) and x < cols - 1:
        yield (x + 1, y)
    if not (cell & 4) and y < rows - 1:
        yield (x, y + 1)
    if not (cell & 8) and x > 0:
        yield (x - 1, y)


def find_shortest_path(
    maze: list[list[int]], start: Coord, goal: Coord
) -> list[Coord]:
    """
    Return the shortest grid path between two cells using BFS.

    Args:
        maze: the game maze, a list of walls.
        start: starting point coordinate.
        goal: destination coordinate.

    Returns:
        A list of coordinate demonstrating the path.
    """
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for neighbor in _get_neighbors(maze, *current):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    if goal not in came_from:
        return []

    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path
