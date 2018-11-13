from enum import Enum
from warnings import warn
from random import choice, randint
from typing import List, Tuple

from consts.colour import Colour
from consts.direction import MovementDirection, DIRECTION_MAGNITUDES
from entity import Entity


class MovementType(Enum):
    """
    What 'brain' controls the movement?
    """
    NONE = 0  # No movement
    CONTROLLED = 1  # Movement is from external source i.e. the player
    PATROL = 2  # Randomly pick a destination around within an area, do this again upon reaching that destination
    CHASE = 3  # Try to move to a target, which itself may be changing it's position i.e. move to attack player


class MovableEntity(Entity):
    """
    An entity that can move
    """
    width_aspect_ratio = 1

    def __init__(self,
                 x: int, y: int, height: int, width: int,
                 base_colour: Colour, tick_rate: int = 5,
                 is_solid: bool = True, parent_collection: List = None,
                 grid_layer: int = 0, movement_type: MovementType = MovementType.PATROL,
                 target = None, target_offset = 0
                 ):
        
        super().__init__(x, y, height, width, base_colour, tick_rate, is_solid, parent_collection, grid_layer)

        self.destination = None
        self.movement_type = movement_type
        self.target = target
        self.target_offset = target_offset
        self.movement_direction = MovementDirection.NONE
        self.last_movement_direction = None
        self.base_speed = 1
        self.speed = self.base_speed
        self.acceleration = 0
        self.max_acceleration = 1
        self.acceleration_rate = 0.01
        
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
        
        def need_to_move(current, lower_bound, middle, upper_bound):
            """
            Check that we even need to move
            :param current:
            :param lower_bound:
            :param middle:
            :param upper_bound:
            :return:
            """
            if current in [lower_bound, middle, upper_bound]:
                return False
            return True
        
        result = False

        if self.movement_type == MovementType.NONE:
            return
    
        if self.movement_type == MovementType.CHASE:
            destination_entity: MovableEntity = Entity.all[self.target]
            self.destination = destination_entity.grid_pixels
        elif self.movement_type == MovementType.CONTROLLED:
            movement_direction = self.movement_direction
            if movement_direction == MovementDirection.NONE:
                self.destination = None
            else: 
                magnitude = DIRECTION_MAGNITUDES[movement_direction]
                self.destination = (self.middle[0] + magnitude[0], self.middle[1] + magnitude[1])
            
        if self.destination is None:
            return result

        move_both = False
    
        move_horizontal, destination_offset_boundary_x = self.is_within_destination_and_offset(
            self.x, self.destination[0]
        )
        
        if move_horizontal:
            move_horizontal = need_to_move(
                self.x, destination_offset_boundary_x[0], self.destination[0], destination_offset_boundary_x[1]
            )
            
        move_vertical, destination_offset_boundary_y = self.is_within_destination_and_offset(
            self.y, self.destination[1]
        )
        
        if move_vertical:
            move_vertical = need_to_move(
                self.y, destination_offset_boundary_y[0], self.destination[1], destination_offset_boundary_y[1]
            )
    
        if move_horizontal and move_vertical:
            move_both = True
            move_horizontal = choice([True, False])
            move_vertical = not move_horizontal
        elif not move_horizontal and not move_vertical:
            self.set_direction(MovementDirection.NONE)
    
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
        elif self.target_offset > 0:
            if current - self.target_offset == destination:
                return False
            elif current + self.target_offset == destination:
                return False
                
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
        """
        Set the direction, if we've changed direction reset our acceleration and speed
        :param direction:
        :return:
        """
        if direction != self.last_movement_direction:
            self.acceleration = 0
            self.speed = 0
            self.last_movement_direction = direction
            self.update_effective_speed()

        self.movement_direction = direction

    def update_effective_speed(self):
        """
        Determine our "speed" if below our base speed then increase by 1 pixel until we breach it.
        Otherwise increase our speed based on our acceleration properties.
        :return:
        """

        if self.speed < self.base_speed:
            self.speed += 1
        else:
            if self.movement_direction != MovementDirection.NONE:
                self.acceleration += self.base_speed * self.acceleration_rate
            else:
                self.acceleration = 0

            if self.acceleration > self.max_acceleration:
                self.acceleration = self.max_acceleration

            self.speed = self.base_speed + self.acceleration

    def move_left(self):
        """
        Move left on screen
        :return:
        """
        self.set_direction(MovementDirection.WEST)
        self.update_effective_speed()
        return self.move_in_direction(-1 * self.speed, 0)


    def move_right(self):
        """
        Move right on screen
        :return:
        """
        self.set_direction(MovementDirection.EAST)
        self.update_effective_speed()
        return self.move_in_direction(self.speed, 0)

    def move_up(self):
        """
        Move up on screen
        :return:
        """
        self.set_direction(MovementDirection.NORTH)
        self.update_effective_speed()
        return self.move_in_direction(0, -1 * self.speed)

    def move_down(self):
        """
        Move down on screen
        :return:
        """
        self.set_direction(MovementDirection.SOUTH)
        self.update_effective_speed()
        return self.move_in_direction(0, self.speed)

    def move_in_direction(self, x_magnitude, y_magnitude):
        """
        If we aren't going to collide with something solid move
        in the specified direction
        :param x_magnitude:
        :param y_magnitude:
        :return:
        """

        def finalise_plane_position(current, destination, magnitude, offset):
            """
            For each of our planes ensure we don't overshoot our destination
            :param current:
            :param destination:
            :param magnitude:
            :param offset:
            :return:
            """
            if magnitude > 0:
                if current + magnitude > destination + offset:
                    return destination + offset
            elif magnitude < 0:
                if current + magnitude < destination - offset:
                    return destination - offset
    
            return current + magnitude

        result = False
        new_direction = self.get_direction(x_magnitude, y_magnitude)

        if self.movement_type == MovementType.CONTROLLED:
            self.destination = (self.x + x_magnitude, self.y + y_magnitude)
    
        collide_entities = self.collide_entities(new_direction, x_magnitude, y_magnitude)
        if len(collide_entities) == 0:
            self.set_direction(new_direction)

            self.x = (self.x + x_magnitude)
            self.y = (self.y + y_magnitude)
            
            # if not controlled movement check we don't overshoot
            if self.movement_type == MovementType.CONTROLLED:
                self.destination = (self.x + x_magnitude, self.y + y_magnitude)
                self.x = (self.x + x_magnitude)
                self.y = (self.y + y_magnitude)
            else:
                self.x = finalise_plane_position(self.x, self.destination[0], x_magnitude, self.target_offset)
                self.y = finalise_plane_position(self.y, self.destination[1], y_magnitude, self.target_offset)

            result = True
            
        self.refresh_dimensions()
        return result

    def collide_entities(self, direction: MovementDirection, x_magnitude, y_magnitude):
        """
        For a given direction and magnitudes, determine which point we need to check for collisions
        and then check if that point will collide if we were to update our position by the passed collisions
        :param direction:
        :param x_magnitude:
        :param y_magnitude:
        :return:
        """
        directions = [self.middle]
        
        # when more accurate collision dection is implemented additional
        # points can be used
        if direction == MovementDirection.NORTH:
            directions = [self.top_middle]
        elif direction == MovementDirection.WEST:
            directions = [self.middle_left]
        elif direction == MovementDirection.EAST:
            directions = [self.middle_right]
        elif direction == MovementDirection.SOUTH:
            directions = [self.bottom_middle]
        else:
            warn(f"Cannot determine point to check collision for direction {direction}")
            return []
            
        for position in directions:
            start_x = position[0]
            start_y = position[1]
        
            collision_items = self.check_collision_point(
                start_x, start_y,
                direction,
                x_magnitude, y_magnitude
            )
        
            if len(collision_items) > 0:
                return collision_items
    
        return []

    # todo move this into colllision module
    def check_collision_point(self, search_x, search_y,
                              direction=MovementDirection.NONE,
                              x_magnitude=0, y_magnitude=0
                              ):
        """
        Check for collision with other entities in the grid
        :param search_x:
        :param search_y:
        :param direction:
        :param x_magnitude:
        :param y_magnitude:
        :return:
        """
        result = []

        # based on our direction which x,y deltas do we need to be looking in?
        magnitudes = DIRECTION_MAGNITUDES[direction]
        collision_items = Entity.grid.query(
            search_x + (magnitudes[0]), search_y + (magnitudes[1]), k = 8, distance_upper_bound = self.width
        )

        if collision_items is not None:
            # todo probably a list comprehension here
            for collision_item in collision_items:
                if not collision_item:
                    continue
                if collision_item[0]:
                    if collision_item[0] == 0:
                        continue
                    if collision_item[0] == self.id:
                        continue

                    collision_entity: Entity = Entity.all[collision_item[0]]

                    if collision_entity.is_solid and direction != MovementDirection.NONE:
                        collision_point = collision_entity.get_point_for_approaching_direction(direction)

                        # clamp but leave 1px difference
                        clamp_x = collision_point[0] - search_x + (DIRECTION_MAGNITUDES[direction][0] * -1)
                        clamp_y = collision_point[1] - search_y + (DIRECTION_MAGNITUDES[direction][1] * -1)

                        # if our clamp distance is greater than our magnitude distance
                        # it means we're close but not yet colliding
                        if direction in [MovementDirection.NORTH, MovementDirection.SOUTH]:
                            if clamp_y != 0 and abs(clamp_y) > abs(y_magnitude):
                                continue

                            self.y += clamp_y
                        
                        elif direction in [MovementDirection.EAST, MovementDirection.WEST]:
                            if clamp_x != 0 and abs(clamp_x) > abs(x_magnitude):
                                continue

                            self.x += clamp_x

                        # set direction to none and refresh since we've clamped
                        self.destination = (self.x, self.y,)
                        self.set_direction(MovementDirection.NONE)
                        self.refresh_dimensions()

                    return self.collide(collision_item[0], collision_item[1])

        return result

    def move_to_point(self, destination_x, destination_y):
        """
        For a destination determine the nearest grid center position and set our direction towards it so that
        we start moving towards it.
        :param destination_x:
        :param destination_y:
        :return:
        """
        grid_destination = Entity.grid.get_pos_for_pixels(destination_x, destination_y)
        self.destination = (grid_destination[0], grid_destination[1])
        self.set_direction(self.get_relative_direction(grid_destination[0], grid_destination[1]))

    def get_relative_direction(self, destination_x, destination_y):
        """
        For an x,y position what is the direction we'd need to travel in to reach the position?
        :param destination_x:
        :param destination_y:
        :return:
        """
        return self.get_direction(destination_x - self.x, destination_y - self.y)

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
