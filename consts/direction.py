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
    MovementDirection.NORTH: (0, -1),
    MovementDirection.SOUTH: (0, 1),
    MovementDirection.EAST: (1, 0),
    MovementDirection.WEST: (-1, 0),
}

DIRECTION_INVERSE = {
    MovementDirection.NORTH: MovementDirection.SOUTH,
    MovementDirection.SOUTH: MovementDirection.NORTH,
    MovementDirection.EAST: MovementDirection.EAST,
    MovementDirection.WEST: MovementDirection.WEST,
}
