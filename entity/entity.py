from enum import Enum
from warnings import warn
from consts.colour import Colour
from consts.direction import MovementDirection, DIRECTION_INVERSE
from typing import List


class Entity:
    
    id = 0
    all = {}
    grid = None
    
    def __init__(
            self,
            x: int, y: int, height: int, width: int,
            base_colour: Colour, tick_rate: float = 0.5,
            is_solid: bool = True, parent_collection: List = None,
            grid_layer = 0,
        ):
        
        Entity.id += 1
        self.id = Entity.id
        
        self.x = x
        self.y = y
        self.last_x = None
        self.last_y = None

        self.height = height
        self.width = width
        self.half_height = height / 2
        self.half_width = width / 2
        self.base_colour = base_colour.value
        self.last_tick = None
        self.tick_rate = tick_rate
        self.is_solid = is_solid
        self.on_collide = None
        self.grid_layer = grid_layer

        self.top_left = None
        self.top_right = None
        self.middle_left = None
        self.middle = None
        self.middle_right = None
        self.bottom_left = None
        self.bottom_right = None
        self.top_middle = None
        self.bottom_middle = None
        self.grid_pixels = None
        self.clip_distance = None
        
        self.refresh_dimensions()
        
        if parent_collection is not None:
            parent_collection.append(self)
            
        Entity.all[self.id] = self
    
    def __str__(self):
        """
        For debug purposes give a textual description of the entity
        :return: str - describing the entity
        """
        return "id: {id} - x: {x}, y: {y} - colour: {colour}".format(
            id = self.id,
            x = self.x,
            y = self.y,
            colour = self.base_colour
        )

    def __repr__(self):
        return self.__str__()

    def refresh_dimensions(self):
        """
        For the current x,y pixel location update all other dimension of the entity
        :return: None
        """

        if self.x == self.last_x and self.y == self.last_y:
            return

        existing_ids = Entity.grid[(self.x, self.y, self.grid_layer.value)]
        matches = existing_ids[(existing_ids != 0) & (existing_ids != self.id)]
        if len(matches) > 0:
            for i in matches:
                other: Entity = Entity.all[i]
                self.collide(i, 0)
                if other.grid_layer == self.grid_layer and other.id != self.id:
                    raise Exception("cannot replace!")

                if other.is_solid:
                    self.x = self.last_x
                    self.y = self.last_y

        self.top_left = (self.x - self.half_width, self.y - self.half_height)
        self.top_middle = (self.x, self.y - self.half_height)
        self.top_right = (self.x + self.half_width, self.y - self.half_height)
        self.bottom_left = (self.x - self.half_width, self.y + self.half_height)
        self.bottom_middle = (self.x, self.y + self.half_height)
        self.bottom_right = (self.x + self.half_width, self.y + self.half_height)
        self.middle_right = (self.x + self.half_width, self.y)
        self.middle_left = (self.x - self.half_width, self.y)
        self.middle = (self.x, self.y)
        self.grid_pixels = Entity.grid.get_pos_for_pixels(self.x, self.y)
        self.clip_distance = self.width * 0.8

        # remove from the grid and re-add to new position
        Entity.grid - self.id
        Entity.grid[(self.x, self.y, self.grid_layer.value)] = self.id

        # update our cached x,y
        self.last_x = self.x
        self.last_y = self.y

    # TODO: move this into colllision module
    def collide(self, other_id, distance):
        """
        Check that we've collided with another entity and if so, call the method associated to the
        on_collide property of the other entity
        
        TODO: there is a limitation that we'll only collide with a maximum of one entity
        
        :param other_id:
        :param distance:
        :return: List[Entity] - Can be an empty list if no collisions
        """
        if other_id != self.id:
            if other_id in Entity.all:
                other_entity = Entity.all[other_id]
                if other_entity.on_collide is not None:
                    # TODO: this should be a we read for other_entiy property for how much overlap we allow before we react
                    if distance < other_entity.half_width:
                        other_entity.on_collide(other_entity, self)
                    # TODO: would there a case for calling our own on collide method?
                    
                if other_entity.is_solid:
                    return [other_entity]
        return []

    def get_point_for_direction(self, direction: MovementDirection):
        """
        For a direction return the pixel x,y for the entity
        :param direction:
        :return: Tuple[int,int] - the pixel point for the direction
        """
        if direction == MovementDirection.SOUTH:
            return self.bottom_middle
        elif direction == MovementDirection.NORTH:
            return self.top_middle
        elif direction == MovementDirection.EAST:
            return self.middle_right
        elif direction == MovementDirection.WEST:
            return self.middle_left

        warn(f"Don't know which point to return for direction {direction}")
        return self.middle

    def get_point_for_approaching_direction(self, direction: MovementDirection):
        """
        For direction return the opposing directions pixel x,y for the entity
        :param direction:
        :return: Tuple[int,int] - the pixel point for the opposing direction
        """
        return self.get_point_for_direction(DIRECTION_INVERSE[direction])

    def get_tick_rate(self):
        """
        What is the entity's tick rate
        :return:
        """
        return self.tick_rate

    def can_think(self, frame_count):
        """
        Check if sufficient time has elapsed for this entity to make another decision.
        Also update the `last_tick` with `frame_count`
        :param frame_count:
        :return:
        """
        if self.last_tick is None:
            self.last_tick = frame_count
            return True

        self.last_tick += frame_count
        
        if self.last_tick > self.get_tick_rate():
            self.last_tick = 0
            return True

        return False

    def think(self, frame_count):
        """
        Make decisions and do things. It's expected you'd override this in classes inheriting from Entity
        :param frame_count:
        :return:
        """
        if not self.can_think(frame_count):
            return False
        
        return True
