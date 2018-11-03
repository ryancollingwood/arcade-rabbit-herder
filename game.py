from grid import Grid
from entity import MovableEntity, Entity, MovementType
from consts import Colour
from consts import Keys


class Game():
    def __init__(self, width, height, tile_size, width_aspect_ratio):
        self.width = width
        self.height = height
        self.tile_size = tile_size

        self.player = None
        self.rabbit = None
        self.npcs = []
        self.items = []
        self.walls = []
        self.score = 0
        self.game_message = ""

        self.grid = Grid(width, height, tile_size)
        
        MovableEntity.width_aspect_ratio = width_aspect_ratio
        Entity.grid = self.grid

        self.load_level()
        
        self.debug_message = ""
        self.game_message = ""

    def reset_game(self):
        self.npcs = []
        self.items = []
        self.walls = []
        self.score = 0
        self.game_message = ""

    def load_level(self):
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

    def add_player(self, row, column):
        x, y = self.grid.get_pixel_center(row, column)
        print("player:", x, y)
        self.player = MovableEntity(x, y, self.tile_size-2, self.tile_size-2, Colour.GREEN, 5)

    def add_rabbit(self, row, column):
        x, y = self.grid.get_pixel_center(row, column)
        print("rabbit:", x, y)
        self.rabbit = MovableEntity(x, y, self.tile_size-2, self.tile_size-2, Colour.WHITE, 5, False, self.npcs)

    def remove_item(self, item):
        self.grid - item.id
        if item in self.items:
            self.items.remove(item)

    def add_speed_down(self, row, column):
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size-2, self.tile_size-2, Colour.RED, 5, False, self.items)
        item.on_collide = self.apply_speed_down

    def apply_speed_down(self, apply_from, apply_to):
        apply_to.tick_rate += 1
        self.remove_item(apply_from)

    def add_speed_up(self, row, column):
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size-2, self.tile_size-2, Colour.LIGHT_BLUE, 5, False, self.items)
        item.on_collide = self.apply_speed_up

    def apply_speed_up(self, apply_from, apply_to):
        apply_to.tick_rate -= 1
        self.remove_item(apply_from)

    def add_carrot(self, row, column):
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size-2, self.tile_size-2, Colour.ORANGE, 5, False, self.items)
        item.on_collide = self.eat_carrot

    def eat_carrot(self, carrot, eater):
        if eater.id != self.rabbit.id:
            return
        self.remove_item(carrot)
        self.score += 1

    def add_end(self, row, column):
        x, y = self.grid.get_pixel_center(row, column)
        item = Entity(x, y, self.tile_size, self.tile_size, Colour.GREY, 5, False, self.items)
        item.on_collide = self.check_end

    def check_end(self, goal, other):
        if other.id != self.rabbit.id:
            return
        self.game_message = "YOU WIN! Press R to restart"

    def start_rabbit(self):
        self.rabbit.target_offset = self.tile_size * 2
        self.rabbit.target = self.player.id
        self.rabbit.movement_type = MovementType.CHASE

    def add_wall(self, row, column):
        # add_at_grid_position
        x, y = self.grid.get_pixel_center(row, column)
        Entity(
            x,
            y,
            self.tile_size, self.tile_size, Colour.BROWN,
            5, True,
            self.walls
        )

    def get_grid_data(self, x, y):
        return self.grid[x, y]

    def debug_x_y(self, x, y):
        print(self.get_grid_data(x, y))
        print(self.grid.query(
            x, y, k = 8, distance_upper_bound = self.tile_size * 2
        ))