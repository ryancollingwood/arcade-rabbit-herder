import warnings
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
        is_solid: bool = True, parent_collection: List = None
        ):
        
        Entity.id += 1
        self.id = Entity.id
        
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.half_height = height / 2
        self.half_width = width / 2
        self.base_colour = base_colour.value
        self.last_tick = None
        self.tick_rate = tick_rate
        self.is_solid = is_solid
        self.on_collide = None

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
        return "{id} - {x},{y} - {colour}".format(
            id = self.id,
            x = self.x,
            y = self.y,
            colour = self.base_colour
        )

    def __repr__(self):
        return self.__str__()

    def refresh_dimensions(self):        
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

        # again check for collision
        
        existing_entity_id = Entity.grid[self.middle] 
        if existing_entity_id != self.id:
            self.collide(existing_entity_id)

        Entity.grid - self.id
        Entity.grid[self.middle] = self.id

    # todo move this into colllision module
    def collide(self, other_id):
        if other_id != self.id:
            if other_id in Entity.all: 
                other_entity = Entity.all[other_id]
                if other_entity.on_collide is not None:
                    other_entity.on_collide(other_entity, self)
                if other_entity.is_solid:
                    return [other_entity]
        return []

    def get_point_for_direction(self, direction: MovementDirection):
        if direction == MovementDirection.SOUTH:
            return self.bottom_middle
        elif direction == MovementDirection.NORTH:
            return self.top_middle
        elif direction == MovementDirection.EAST:
            return self.middle_left
        elif direction == MovementDirection.WEST:
            return self.middle_right

        warnings.warn(f"Don't know which point to return for direction {direction}")
        return self.middle

    def get_point_for_approaching_direction(self, direction: MovementDirection):
        return self.get_point_for_direction(DIRECTION_INVERSE[direction])

    def can_think(self, frame_count):
        if self.last_tick is None:
            self.last_tick = frame_count
            return True

        self.last_tick += frame_count
        
        if self.last_tick > self.tick_rate:
            self.last_tick = 0
            return True

        return False

    def think(self, frame_count):
        if self.can_think(frame_count):
            #self.last_tick = frame_count
            # this was added to get around current grid implementation
            # only support one thing in the data layer at a time
            self.refresh_dimensions()
        else:
            return False
        
        return True
