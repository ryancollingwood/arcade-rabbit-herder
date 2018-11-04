from entity import Entity
from consts.colour import Colour
from typing import List, Tuple
from random import choice, randint
from enum import Enum


class MovementType(Enum):
    NONE = 0
    CONTROLLED = 1
    PATROL = 2
    CHASE = 3


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


class MovableEntity(Entity):
    
    width_aspect_ratio = 1

    direction_magnitues = {
        MovementDirection.NORTH : (0,-1),
        MovementDirection.SOUTH : (0,1),
        MovementDirection.EAST: (1,0),
        MovementDirection.WEST: (-1,0),
    }

    def __init__(self,
                 x: int, y: int, height: int, width: int,
                 base_colour: Colour, tick_rate: int = 5,
                 is_solid: bool = True, parent_collection: List = None,
                 movement_type: MovementType = MovementType.PATROL,
                 target = None, target_offset = 0
                 ):
        
        super().__init__(x, y, height, width, base_colour, tick_rate, is_solid, parent_collection)

        self.destination = None
        self.movement_type = movement_type
        self.target = target
        self.target_offset = target_offset
        self.movement_direction = MovementDirection.NONE
        self.movement_speed = 1
        
    def think(self, frame_count):
        """
        If we can think then move
        :return:
        """
        if super().think(frame_count):
            self.move()

    def move(self):
        """
        Determine which direction we should move and conditionally set our destination
        :return:
        """
        result = False

        if self.movement_type == MovementType.NONE:
            return
    
        if self.movement_type == MovementType.CHASE:
            destination_entity = Entity.all[self.target]
            self.destination = (destination_entity.x, destination_entity.y)
        elif self.movement_type == MovementType.CONTROLLED:
            movement_direction = self.movement_direction
            if movement_direction == MovementDirection.NONE:
                self.destination = None
            else: 
                magnitude = MovableEntity.direction_magnitues[movement_direction]
                self.destination = (self.middle[0] + magnitude[0], self.middle[1] + magnitude[1])        
            
        if self.destination is None:
            return result

        move_both = False
    
        move_horizontal, destination_offset_boundary_x = self.is_within_destination_and_offset(
            self.x, self.destination[0]
        )
        move_vertical, destination_offset_boundary_y = self.is_within_destination_and_offset(
            self.y, self.destination[1]
        )
    
        if move_horizontal and move_vertical:
            move_both = True
            move_horizontal = choice([True, False])
            move_vertical = not move_horizontal
    
        if move_horizontal:
            result = self.move_in_plane(
                self.x, self.destination[0], destination_offset_boundary_x, self.move_left, self.move_right
                )

            if not result and move_both:
                result = self.move_in_plane(
                    self.y, self.destination[1], destination_offset_boundary_y, self.move_up, self.move_down
                    )

            return result
        
        elif move_vertical:
            result = self.move_in_plane(
                self.y, self.destination[1], destination_offset_boundary_y, self.move_up, self.move_down
                )
            
            if not result and move_both:
                result = self.move_in_plane(
                    self.x, self.destination[0], destination_offset_boundary_x, self.move_left, self.move_right
                    )

        
            return result
        else:
            
            if self.movement_type == MovementType.PATROL:
                # TODO: Not use a hardcoded range
                self.destination = (randint(0, 200), randint(0, 200))
    
        return False

    def move_in_plane(self,
                      current: int, destination: int,
                      destination_offset_boundary: Tuple[int, int],
                      decrease_position,
                      increase_position):
        """
        For a plane (x-axis or y-axis) should we increase our position or decrease our position
        :param current: current value in the plane
        :param destination: destination value in the plane
        :param destination_offset_boundary: the offset boundaries (min, max)
        :param decrease_position: function to decrease our position in the boundary
        :param increase_position: function to increase our position in the boundary
        :return:
        """
        result = False
        
        if current < destination_offset_boundary[0]:
            result = increase_position()
        elif destination_offset_boundary[0] < current < destination:
            result = decrease_position()
        elif current > destination_offset_boundary[1]:
            result = decrease_position()
        elif destination < current < destination_offset_boundary[1]:
            result = increase_position()
        elif self.target_offset > 0 and current == destination:
            # tie breaking if we're exactly on our target but we need to be at an offset
            if choice([True, False]):
                result = decrease_position()
            else:
                result = increase_position()
                
        return result

    def is_within_destination_and_offset(self, current_value, target_value):
        """
        For a plane (x-axis or y-axis) are we within the target and the target +/- the offset
        :param current_value:
        :param target_value:
        :return: bool are we within the boundary, tuple of the boundary
        """
        destination_bounds = (target_value - self.target_offset, target_value + self.target_offset)
        
        if current_value != target_value and (
                (current_value != destination_bounds[0]) or (current_value != destination_bounds[1])
                ):
            return True, destination_bounds
        
        return False, destination_bounds

    def set_direction(self, direction: MovementDirection):
        self.movement_direction = direction

    def move_left(self):
        """
        Move left on screen
        :return:
        """
        return self.move_in_direction(-1 * self.movement_speed, 0)

    def move_right(self):
        """
        Move right on screen
        :return:
        """
        return self.move_in_direction(1 * self.movement_speed, 0)

    def move_up(self):
        """
        Move up on screen
        :return:
        """
        return self.move_in_direction(0, -1 * self.movement_speed)

    def move_down(self):
        """
        Move down on screen
        :return:
        """
        return self.move_in_direction(0, 1 * self.movement_speed)

    def move_in_direction(self, x_magnitude, y_magnitude):
        """
        If we aren't going to collide with something solid move
        in the specified direction
        :param x_magnitude:
        :param y_magnitude:
        :return:
        """
        result = False
        new_direction = self.get_direction(x_magnitude, y_magnitude)
    
        collide_entities = self.collide_entities(new_direction)
        if collide_entities is not None and len(collide_entities) == 0:
            Entity.grid - self.id
            self.movement_direction = new_direction
            self.x = (self.x + x_magnitude) #% MovableEntity.width_aspect_ratio
            self.y = (self.y + y_magnitude) #% MovableEntity.width_aspect_ratio
            result = True
            
        self.refresh_dimensions()
        return result

    def collide_entities(self, direction: MovementDirection):
    
        directions = [self.middle]
        
        # when more accurate collision dection is implemented additional
        # points can be used
        if direction == MovementDirection.NORTH:
            #directions = [self.top_left, self.top_middle, self.top_right]
            directions = [self.top_middle]
        elif direction == MovementDirection.WEST:
            #directions = [self.top_left, self.bottom_left, self.middle_left]
            directions = [self.middle_left]
        elif direction == MovementDirection.EAST:
            #directions = [self.top_right, self.bottom_right, self.middle_right]
            directions = [self.middle_right]
        elif direction == MovementDirection.SOUTH:
            #directions = [self.bottom_right, self.bottom_left, self.bottom_middle]
            directions = [self.bottom_middle]
            
        for position in directions:
            start_x = position[0]
            start_y = position[1]
        
            collision_item = self.check_collision_point(start_x, start_y)
        
            if len(collision_item) > 0:
                #game_state.debug_message = str(collision_item[0].middle)
                return collision_item
    
        return []

    @staticmethod
    def get_direction(x_magnitude, y_magnitude):
        """
        For a given change in x,y what's the direction
        :param x_magnitude:
        :param y_magnitude:
        :return:
        """
        new_direction = MovementDirection.NONE
        if x_magnitude == 0:
            if y_magnitude < 0:
                new_direction = MovementDirection.NORTH
            elif y_magnitude > 0:
                new_direction = MovementDirection.SOUTH
        elif y_magnitude == 0:
            if x_magnitude < 0:
                new_direction = MovementDirection.WEST
            elif x_magnitude > 0:
                new_direction = MovementDirection.EAST
        else:
            if y_magnitude < 0:
                if x_magnitude > 0:
                    new_direction = MovementDirection.NORTH_EAST
                elif x_magnitude < 0:
                    new_direction = MovementDirection.NORTH_WEST
            elif y_magnitude > 0:
                if x_magnitude > 0:
                    new_direction = MovementDirection.SOUTH_EAST
                elif x_magnitude < 0:
                    new_direction = MovementDirection.SOUTH_WEST
        return new_direction


