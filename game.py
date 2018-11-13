from grid import Grid
from entity import MovableEntity, Entity, MovementType
from consts import Colour
from consts import Layer


class Game():
    def __init__(
            self, width, height, tile_size, width_aspect_ratio: float,
            grid_layers: int = 3, flip_x: bool = False, flip_y: bool = False):

        self.is_running: bool = False
        self.width: int = width
        self.height: int = height
        self.tile_size: float = tile_size
        self.grid_layers: int = grid_layers
        self.flip_x: bool = flip_x
        self.flip_y: bool = flip_y

        self.player: MovableEntity = None
        self.rabbit: MovableEntity = None
        self.npcs = []
        self.items = []
        self.walls = []
        self.score: int = 0
        self.game_message = ""

        self.grid = None
        
        MovableEntity.width_aspect_ratio = width_aspect_ratio

        self.load_level()

    def reset_game(self):
        """
        Restart the game and reset the game level
        :return:
        """
        self.is_running = False
        self.player = None
        self.rabbit = None
        self.npcs = []
        self.items = []
        self.walls = []
        self.score = 0
        self.game_message = ""
        self.debug_message = ""

        # reset and reassign the grid
        self.grid = Grid(self.width, self.height, self.tile_size, self.grid_layers, self.flip_x, self.flip_y)
        Entity.grid = self.grid

    def load_level(self):
        """
        Load the level
        :return:
        """
        self.reset_game()

        with open('level.txt') as f:
            wall_lines = f.readlines()        
        
        for row_index, row_value in enumerate(wall_lines):            
            for col_index, col_value in enumerate(row_value):
                if col_value == "#":
                    self.add_wall(row_index, col_index)
                elif col_value == "@":
                    self.add_player(row_index, col_index)
                elif col_value == "&":
                    self.add_rabbit(row_index, col_index)
                elif col_value == ".":
                    self.add_speed_down(row_index, col_index)
                elif col_value == "*":
                    self.add_speed_up(row_index, col_index)
                elif col_value == "~":
                    self.add_carrot(row_index, col_index)
                elif col_value == "X":
                    self.add_end(row_index, col_index)
        
        self.start_rabbit()
        self.is_running = True

    def add_player(self, row, column):
        """
        Add the player to game map
        :param row:
        :param column:
        :return:
        """
        x, y = self.grid.get_pixel_center(row, column)
        
        self.player = MovableEntity(
            x, y, self.tile_size-2, self.tile_size-2,
            Colour.GREEN, 0.10,
            is_solid = True, parent_collection = None,
            grid_layer = Layer.PLAYER
        )

        self.player.movement_type = MovementType.CONTROLLED
        self.player.base_speed = 5
        self.player.max_acceleration = 10
        self.player.acceleration_rate = 0.25

    def add_rabbit(self, row, column):
        """
        Add the rabbit to the game map
        :param row:
        :param column:
        :return:
        """
        x, y = self.grid.get_pixel_center(row, column)
        
        self.rabbit = MovableEntity(
            x, y, self.tile_size-2, self.tile_size-2,
            Colour.WHITE, 0.10, False, self.npcs,
            grid_layer = Layer.NPC
        )
        self.rabbit.base_speed = 4
        self.rabbit.max_acceleration = 8
        self.rabbit.acceleration_rate = 0.5

    def remove_item(self, item):
        """
        Remove an item from the game map
        :param item:
        :return:
        """
        self.grid - item.id
        if item in self.items:
            self.items.remove(item)

    def add_speed_down(self, row, column):
        """
        Add a speed down item to the game map
        :param row:
        :param column:
        :return:
        """
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size-2, self.tile_size-2, Colour.RED, 5, False, self.items, Layer.ITEMS)
        item.on_collide = self.apply_speed_down

    def apply_speed_down(self, apply_from, apply_to):
        """
        On an entity `apply_to` colliding with `apply_from` apply a speed down to `apply_to` and remove `apply_from`
        from the game map
        :param apply_from:
        :param apply_to:
        :return:
        """
        try:
            acceleration_modifier = apply_to.acceleration_rate / 2
            apply_to.acceleration_rate -= acceleration_modifier
        except AttributeError:
            print("tried to apply speed down wrong thing?", apply_to, type(apply_to))
            return
        self.remove_item(apply_from)

    def add_speed_up(self, row, column):
        """
        Add a speed up item to the game map
        :param row:
        :param column:
        :return:
        """
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size-2, self.tile_size-2, Colour.LIGHT_BLUE, 5, False, self.items, Layer.ITEMS)
        item.on_collide = self.apply_speed_up

    def apply_speed_up(self, apply_from, apply_to):
        """
        On an entity `apply_to` colliding with `apply_from` apply a speed up to `apply_to` and remove `apply_from`
        from the game map
        :param apply_from:
        :param apply_to:
        :return:
        """
        try:
            acceleration_modifier = apply_to.acceleration_rate / 2
            apply_to.acceleration_rate += acceleration_modifier
        except AttributeError:
            print("tried to apply speed up wrong thing?", apply_to, type(apply_to))
            return
        self.remove_item(apply_from)

    def add_carrot(self, row, column):
        """
        Add a carrot to the game map
        :param row:
        :param column:
        :return:
        """
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size-2, self.tile_size-2, Colour.ORANGE, 5, False, self.items, Layer.ITEMS)
        item.on_collide = self.eat_carrot

    def eat_carrot(self, carrot, eater):
        """
        If `eater` is our rabbit, then remove carrot from the game map and increase the score
        :param carrot:
        :param eater:
        :return:
        """
        if eater.id != self.rabbit.id:
            return
        self.remove_item(carrot)
        self.score += 1

    def add_end(self, row, column):
        """
        Add the end/goal to the game map
        :param row:
        :param column:
        :return:
        """
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size, self.tile_size, Colour.GREY, 5, False, self.items, Layer.WORLD)
        item.on_collide = self.check_end

    def check_end(self, goal, other):
        """
        If something collides with the goal check if it's the rabbit
        If it is the rabbit then we've completed the level
        :param goal:
        :param other:
        :return:
        """
        if other.id != self.rabbit.id:
            return
        self.game_message = "YOU WIN! Press R to restart"
        print(self.game_message)

    def start_rabbit(self):
        """
        Make the rabbit follow the player, set the rabbits target to be the player and set it's `target_offset`
        :return:
        """
        self.rabbit.target_offset = self.tile_size * 2
        self.rabbit.target = self.player.id
        self.rabbit.movement_type = MovementType.CHASE
        self.rabbit.movement_speed = 3

    def add_wall(self, row, column):
        """
        Add a wall to the game world
        DEPRECIATED - Walls are being rendered as a single shape
        :param row:
        :param column:
        :return:
        """
        # add_at_grid_position
        x, y = self.grid.get_pixel_center(row, column)
        Entity(
            x,
            y,
            self.tile_size, self.tile_size, Colour.BROWN,
            5, True,
            self.walls,
            Layer.WORLD
        )

    def get_grid_data(self, x, y):
        """
        Get the data in our grid at a given x,y pixel position
        :param x:
        :param y:
        :return:
        """
        return self.grid[x, y]

    def debug_x_y(self, x, y):
        """
        Print out debug information our grid at a given x,y pixel position
        :param x:
        :param y:
        :return:
        """
        print("id:", self.get_grid_data(x, y))
        print("nearby:", self.grid.query(
            x, y, k = 8, distance_upper_bound = self.tile_size * 2
        ))