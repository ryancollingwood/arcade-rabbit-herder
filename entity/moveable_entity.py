from warnings import warn
from random import choice, randint
from typing import List, Tuple

from consts.colour import Colour
from consts.direction import MovementDirection, DIRECTION_MAGNITUDES
from consts.movement_type import MovementType
from entity import Entity
from pathfinding import astar


class MovableEntity(Entity):
    """
    An entity that can move
    """
    width_aspect_ratio = 1
    
    def __init__(self,
                 x: int, y: int, height: int, width: int,
                 base_colour: Colour, tick_rate: float = 5.0,
                 is_solid: bool = True, parent_collection: List = None,
                 grid_layer: int = 0, entity_type_id: int = 0, movement_type: MovementType = MovementType.PATROL,
                 target = None, target_offset = 0
                 ):
        
        super().__init__(x, y, height, width, base_colour, tick_rate, is_solid,
                         parent_collection, grid_layer, entity_type_id)
        
        self.destination = None
        self.last_destination = None
        self.movement_type = movement_type
        self.target = target
        self.target_offset = target_offset
        self.original_target_offset = target_offset
        self.movement_direction = MovementDirection.NONE
        self.last_movement_direction = None
        self.base_speed = 1
        self.speed = self.base_speed
        self.acceleration = 0
        self.max_acceleration = 1
        self.acceleration_rate = 0.01
        self.path = None
        self.path_step = None
        self.find_path_if_stuck = False
    
    def think(self, frame_count):
        """
        If we can think then move
        :return:
        """
        if super().think(frame_count):
            self.move()
    
    @staticmethod
    def need_to_move_in_plane(current, lower_bound, middle, upper_bound):
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
    
    def need_to_move_horizontal(self, target_xy, destination_bounds_x = None):
        """
        Do we need to make changes on the horizontal plane to get to our destination?
        :return:
        """
        move_horizontal, destination_bounds_x = self.is_within_destination_and_offset(
            self.x, target_xy[0], destination_bounds_x
        )
        
        return move_horizontal
    
    def need_to_move_vertical(self, target_xy, destination_bounds_y = None):
        """
        Do we need to make changes on the vertical plane to get to our destination?
        :return:
        """
        move_vertical, destination_bounds_y = self.is_within_destination_and_offset(
            self.y, target_xy[1], destination_bounds_y
        )
        
        return move_vertical
    
    def move(self):
        """
        Determine which direction we should move and conditionally set our destination
        :return:
        """
        result = False
        
        destination = self.get_destination()
        
        if self.destination != destination:
            self.last_destination = self.destination
            self.destination = destination
        
        if destination is None:
            return result
        
        move_both = False

        destination_offset_boundary_x, destination_offset_boundary_y = self.get_destination_bounds()
        
        move_horizontal = self.need_to_move_horizontal(self.destination, destination_offset_boundary_x)
        move_vertical = self.need_to_move_vertical(self.destination, destination_offset_boundary_y)
        
        if move_horizontal and move_vertical:
            move_both = True
            move_horizontal = choice([True, False])
            move_vertical = not move_horizontal
        elif not move_horizontal and not move_vertical:
            # we've probably arrived at our destination
            # TODO: raise an event
            self.set_direction(MovementDirection.NONE)
            if self.path:
                self.reset_path()
        
        if move_horizontal:
            result = self.move_in_plane(
                self.x, self.destination[0], destination_offset_boundary_x, self.move_left, self.move_right
            )
            
            if not result and move_both:
                result = self.move_in_plane(
                    self.y, self.destination[1], destination_offset_boundary_y, self.move_up, self.move_down
                )

            self.find_chasing_path(result)
            
            return result
        
        elif move_vertical:
            result = self.move_in_plane(
                self.y, self.destination[1], destination_offset_boundary_y, self.move_up, self.move_down
            )
            
            if not result and move_both:
                result = self.move_in_plane(
                    self.x, self.destination[0], destination_offset_boundary_x, self.move_left, self.move_right
                )

            self.find_chasing_path(result)

            return result
        else:
            
            if self.movement_type == MovementType.PATROL:
                # pick a point near our original position modified by our target offset value
                half_offset = self.target_offset // 2
                self.destination = (
                    randint(self.original_x - half_offset, self.original_x + half_offset),
                    randint(self.original_y - half_offset, self.original_y + half_offset)
                )
        
        return False

    def find_chasing_path(self, result):
        """
        Are able to move towards our target? If not then use path finding to stop us from getting stuck
        :param result:
        :return:
        """
        if self.find_path_if_stuck:
            destination_entity = Entity.all[self.target]

            if not result:
                if not self.path or destination_entity.grid_pixels not in self.path:
                    path_to_target = self.get_path(destination_entity.grid_pixels[0], destination_entity.grid_pixels[1])
                    if destination_entity.grid_pixels in path_to_target:
                        self.reset_path(path_to_target)
                    else:
                        # warn("couldn’t get back on track")
                        if self.is_try_to_follow_find_path():
                            self.reset_path(path_to_target)
            else:
                if self.path and self.destination == destination_entity.grid_pixels:
                    self.reset_path()
                        
    def is_try_to_follow_find_path(self):
        """
        If we chasing and then get a path that doesn't lead to our target do we follow it?
        Expected to be overridden in child classes
        :return:
        """
        return choice([True, False])

    def get_destination_target(self):
        """
        Convert our target (which) is an int to the entity associated to that int.
        :return:
        """
        destination_entity = None
        
        if self.movement_type == MovementType.NONE:
            return destination_entity
        
        if self.target is not None:
            try:
                destination_entity: MovableEntity = Entity.all[self.target]
            except IndexError as e:
                # this could happen if we were chasing an item that has been
                # eaten by someone else
                warn(f"Target {self.target} not found in grid")
                warn(e)
                return None
        
        return destination_entity
    
    def get_destination(self):
        """
        Determine our new destination
        :return:
        """
        
        def get_path_to_destination():
            """
            This is a hack, to compensate for pathfinding timing out without finding the final_destination
            IF we get a path without the destination then DONT reset as we might be able to get close enough by
            following our existing path
            :return:
            """
            new_path = self.get_path(final_destination[0], final_destination[1])
            
            # this is a hack in the case of path-finding timing out
            if new_path is not None and final_destination in new_path:
                self.reset_path(new_path)
            else:
                # exisiting path if any if preserved
                pass

        if self.movement_type == MovementType.NONE:
            return None

        destination = None
        destination_entity = self.get_destination_target()
        
        if destination_entity and self.movement_type in [MovementType.CHASE, MovementType.PATH]:
            destination = destination_entity.grid_pixels
        
        if self.movement_type == MovementType.PATH:
            # set the target offset to 0 s that we move along points
            # having a target offset may mean we don’t progress to the next point
            
            # TODO: incorporate offset into final_destination calculation
            final_destination = destination_entity.grid_pixels
            distance_to_final_final_destination = Entity.grid.get_straight_line_distances_between_pixels(
                self.middle, destination_entity.middle
            )
            
            # if our target is soild we cannot actually stand on them
            # TODO: this assumes no entity is every bigger than Grid.tile_size in size
            if destination_entity.is_solid and distance_to_final_final_destination <= Entity.grid.tile_size:
                self.reset_path()
                return None
            
            if not self.path:
                get_path_to_destination()
            
            if self.path:
                if final_destination not in self.path:
                    # continue on our current path as it will probably get as closer to the
                    # destination anyways TODO: Make this a configurable setting?
                    if self.path_step < len(self.path) - 1:
                        # if our target is further than our original offset value then invalidate our current path
                        if distance_to_final_final_destination > self.original_target_offset:
                            self.reset_path()
                        else:
                            pass
                    else:
                        # if we've reached our destination, then reset the path
                        # TODO raise that we need a new target
                        self.reset_path()
            
        if self.path and self.movement_type != MovementType.PATH:
            # if we have a path, but our movement type is not to explicitly follow the path
            # then check we are in range then stop the path
            # if you evaluate this for `self.movement_type == MovementType.PATH`
            # then it will always reset as the current target is the next step in the path
            if not self.need_to_move_horizontal(destination_entity.grid_pixels) and \
                    not self.need_to_move_vertical(destination_entity.grid_pixels):
                self.reset_path()

        if self.path:
            if self.path_step < len(self.path):
                # can we progress on the path?
                destination = self.path[self.path_step]
                
                move_horizontal = self.need_to_move_horizontal(destination, [destination[0], destination[0]])
                move_vertical = self.need_to_move_vertical(destination, [destination[1], destination[1]])
                
                if not move_horizontal and not move_vertical:
                    self.path_step += 1
                    if self.path_step != len(self.path):
                        destination = self.path[self.path_step]
            
            elif self.movement_type == MovementType.PATH:
                get_path_to_destination()
            else:
                self.reset_path()
        
        if self.movement_type == MovementType.CONTROLLED:
            movement_direction = self.movement_direction
            if movement_direction == MovementDirection.NONE:
                destination = None
            else:
                magnitude = DIRECTION_MAGNITUDES[movement_direction]
                destination = (self.middle[0] + magnitude[0], self.middle[1] + magnitude[1])
        
        return destination
    
    def reset_path(self, new_path = None):
        """
        Reset our current path
        :return:
        """
        if new_path is None:
            self.path = None
            self.path_step = None
        else:
            self.path = new_path
            self.path_step = 0
    
    def get_path(self, x, y):
        """
        Get a path to the target x,y - which will be looked up to row, column for A* purposes
        :return:
        """
        end_row, end_column = Entity.grid.get_column_row_for_pixels(x, y)
        start_row, start_column = Entity.grid.get_column_row_for_pixels(self.x, self.y)
        
        # TODO this will fail if any of thses are 0
        if start_row and start_column and end_row and end_column:
            path = astar(Entity.grid.grid_for_pathing(), (start_row, start_column), (end_row, end_column))
            
            if path:
                # convert from row,col to pixels
                return [Entity.grid.get_pixel_center(p[0], p[1]) for p in path]
        
        return None
    
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
    
    def is_within_destination_and_offset(self, current_value, target_value, destination_bounds = None):
        """
        For a plane (x-axis or y-axis) are we within the target and the target +/- the offset
        :param current_value:
        :param target_value:
        :param destination_bounds: Optional will be calculated by a call to get_plane_bounds if not supplied
        :return: bool are we within the boundary, tuple of the boundary
        """
        if destination_bounds is None:
            destination_bounds = self.get_plane_bounds(target_value)
            
        if self.need_to_move_in_plane(current_value, destination_bounds[0], target_value, destination_bounds[1]):
            return True, destination_bounds
            
        return False, destination_bounds

    def get_plane_bounds(self, plane_target_value, plane_offset = None):
        """
        :param plane_target_value: the value in the x or y plane we're targetting
        :return:
        """
        if plane_offset is None:
            plane_offset = self.target_offset
            
        destination_bounds = (plane_target_value - plane_offset, plane_target_value + plane_offset)
        return destination_bounds
    
    def get_destination_bounds(self):
        """
        Helper method to get the x,y bounds for our current destination
        :return: x_bounds, y_bounds
        """
        plane_offset = self.get_target_offset()
        
        x_bounds = self.get_plane_bounds(self.destination[0], plane_offset)
        y_bounds = self.get_plane_bounds(self.destination[1], plane_offset)
        
        return x_bounds, y_bounds

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
            # TODO: Here we can check if we're moving on a path and allow overshooting if overshoot is still on the path
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
            
            self.set_x(self.x + x_magnitude)
            self.set_y(self.y + y_magnitude)
            
            # if not controlled movement check we don't overshoot
            if self.movement_type == MovementType.CONTROLLED:
                self.destination = (self.x + x_magnitude, self.y + y_magnitude)
                self.set_x(self.x + x_magnitude)
                self.set_y(self.y + y_magnitude)
            else:
                if self.destination:
                    
                    offset = self.get_target_offset()
                    
                    self.set_x(finalise_plane_position(self.x, self.destination[0], x_magnitude, offset))
                    self.set_y(finalise_plane_position(self.y, self.destination[1], y_magnitude, offset))
            
            result = True
        
        self.refresh_dimensions()
        return result

    def get_target_offset(self):
        """
        Get the target offset for moving towards our destination. If we have a path with our destination in it, then
        we ignore self.target_offset and return 0
        :return:
        """
        if self.path and self.destination in self.path:
            return 0
        
        return self.target_offset
    
    def collide_entities(self, direction: MovementDirection, x_magnitude, y_magnitude):
        """
        For a given direction and magnitudes, determine which point we need to check for collisions
        and then check if that point will collide if we were to update our position by the passed collisions
        :param direction:
        :param x_magnitude:
        :param y_magnitude:
        :return:
        """
        
        # when more accurate collision detection is implemented additional
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
    
    # TODO: move this into collision module
    def check_collision_point(self, search_x, search_y,
                              direction = MovementDirection.NONE,
                              x_magnitude = 0, y_magnitude = 0
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
                            
                            self.set_y(self.y + clamp_y)
                        
                        elif direction in [MovementDirection.EAST, MovementDirection.WEST]:
                            if clamp_x != 0 and abs(clamp_x) > abs(x_magnitude):
                                continue
                            
                            self.set_x(self.x + clamp_x)
                        
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
