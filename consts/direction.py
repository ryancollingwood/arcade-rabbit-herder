from enum import Enum


class MovementDirection(Enum):
    SOUTH_WEST = 1
    SOUTH = 2
    SOUTH_EAST = 3
    WEST = 4
    NONE = 5
    EAST = 6
    NORTH_WEST = 7
    NORTH = 8
    NORTH_EAST = 9


DIRECTION_MAGNITUDES = {
    MovementDirection.NORTH_WEST: (-1, -1),
    MovementDirection.NORTH: (0, -1),
    MovementDirection.NORTH_EAST: (1, -1),
    MovementDirection.EAST: (1, 0),
    MovementDirection.SOUTH_EAST: (1, 1),
    MovementDirection.SOUTH: (0, 1),
    MovementDirection.SOUTH_WEST: (-1, 1),
    MovementDirection.WEST: (-1, 0),
}

DIRECTION_INVERSE = {
    MovementDirection.NORTH_WEST: MovementDirection.SOUTH_EAST,
    MovementDirection.NORTH: MovementDirection.SOUTH,
    MovementDirection.NORTH_EAST: MovementDirection.SOUTH_WEST,
    MovementDirection.EAST: MovementDirection.WEST,
    MovementDirection.SOUTH_EAST: MovementDirection.NORTH_WEST,
    MovementDirection.SOUTH: MovementDirection.NORTH,
    MovementDirection.SOUTH_WEST: MovementDirection.NORTH_EAST,
    MovementDirection.WEST: MovementDirection.EAST,
}
