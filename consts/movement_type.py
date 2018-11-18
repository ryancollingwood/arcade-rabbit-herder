from enum import Enum


class MovementType(Enum):
    """
    What 'brain' controls the movement?
    """
    NONE = 0  # No movement
    CONTROLLED = 1  # Movement is from external source i.e. the player
    PATROL = 2  # Randomly pick a destination around within an area, do this again upon reaching that destination
    CHASE = 3  # Try to move to a target, which itself may be changing it's position i.e. move to attack player
    PATH = 4  # Given a target get a path to it