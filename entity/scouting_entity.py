from typing import List
from .entity import Entity
from .moveable_entity import MovableEntity
from consts.movement_type import MovementType
from consts.colour import Colour


class ScoutingEntity(MovableEntity):
    def __init__(
            self, x: int, y: int, height: int, width: int,
            base_colour: Colour, tick_rate: float = 5,
            is_solid: bool = True, parent_collection: List = None,
            grid_layer: int = 0, entity_type_id: int = 0, movement_type: MovementType = MovementType.PATROL,
            target = None, target_offset = 0, search_for_entity_types: List[int] = None, search_tile_range = 1
    ):
        super().__init__(
            x, y, height, width, base_colour, tick_rate, is_solid, parent_collection, grid_layer, entity_type_id,
            movement_type, target, target_offset
        )
        
        self.search_for_entity_types = None
        self.search_distance = Entity.grid.tile_size * search_tile_range
        self.set_search_for_entity_types(search_for_entity_types)
        
        self.original_movement_type = movement_type
        self.original_target = self.target
    
    def set_search_for_entity_types(self, value):
        self.search_for_entity_types = value
    
    def get_destination_target(self):
        """
        If we have a path check and ends in grid position of an entity of interest.
        If not then see if there are any entities of interest in a tile radius around us.
        If is then return the first as our target.

        Need to handle the case of multiple candidates.
        Currently doesn't have a notion of line of sight.
        :return:
        """
        # first check if we have a path, does it end in a entity of interest
        
        def get_nearby_interesting(results, search_for_entity_types):

            if not search_for_entity_types:
                return list()

            return [
                x[0] for x in results if
                x[0] > 0 and Entity.all[int(x[0])].entity_type_id in search_for_entity_types
            ]
        
        if self.path:
            last_step = self.path[-1]
            last_step_match = Entity.grid.query(last_step[0], last_step[1], k = 1)
            last_step_nearby_match = get_nearby_interesting(last_step_match, self.search_for_entity_types)
            if len(last_step_nearby_match) > 0:
                self.target = int(last_step_nearby_match[0])
                return Entity.all[last_step_nearby_match[0]]
        
        # look for things of interest that are in range
        nearby = Entity.grid.query(self.x, self.y, k = 16, distance_upper_bound = self.search_distance)
        nearby_interesting = get_nearby_interesting(nearby, self.search_for_entity_types)
        
        self.movement_type = self.original_movement_type
        self.target_offset = self.original_target_offset

        # TODO: if we can get a path to any of them, then that's our destination for now just get the first
        if len(nearby_interesting) > 0 and self.target == self.original_target:
            self.movement_type = MovementType.PATH
            self.target = int(nearby_interesting[0])
            return Entity.all[nearby_interesting[0]]
        else:
            if len(nearby_interesting) == 0:
                self.target = self.original_target
                if self.movement_type != self.original_movement_type and self.path:
                    # given we've already not found anything interesting call the super version
                    destination_entity = super().get_destination_target()
                    if destination_entity.grid_pixels not in self.path:
                        self.reset_path()
                    return destination_entity
        
        # if no destination then use super().get_destination
        return super().get_destination_target()
