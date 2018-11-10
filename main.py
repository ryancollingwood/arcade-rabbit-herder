# Library imports
import arcade

from game import Game
from entity import Entity, MovementType
from consts.colour import Colour
from entity import MovableEntity
from consts.direction import MovementDirection

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 25

COLOUR_MAP = {
    Colour.BLACK.value: arcade.color.BLACK,
    Colour.BROWN.value: arcade.color.BROWN,
    Colour.DARK_BLUE.value: arcade.color.DARK_BLUE,
    Colour.DARK_GREY.value: arcade.color.DARK_GRAY,
    Colour.GREEN.value: arcade.color.GREEN,
    Colour.GREY.value: arcade.color.GRAY,
    Colour.LIGHT_BLUE.value: arcade.color.BABY_BLUE_EYES,
    Colour.LIGHT_GREEN.value: arcade.color.LIGHT_GREEN,
    Colour.MAROON.value: arcade.color.MAROON,
    Colour.ORANGE.value: arcade.color.ORANGE,
    Colour.PURPLE.value: arcade.color.PURPLE,
    Colour.RED.value: arcade.color.RED,
    Colour.TAN.value: arcade.color.TAN,
    Colour.WHITE.value: arcade.color.WHITE,
    Colour.YELLOW.value: arcade.color.YELLOW,
}

class MyGame(arcade.Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.set_update_rate(1 / 20)

        arcade.set_background_color(arcade.color.BLACK)

        self.game = None
        # If you have sprite lists, you should create them here,
        # and set them to None
        self.shape_walls = None

    def setup(self):
        # Create your sprites and sprite lists here
        self.game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, 1, grid_layers = 4)

        self.shape_walls = arcade.ShapeElementList()

        self.game.game_message = "Lead the Rabbit home"

        point_list = []
        color_list = []

        # create the walls into a single shape
        walls = self.game.walls
        for wall in walls:
            points = self.get_entity_dimensions(wall)
            point_list.append(points[0])
            point_list.append(points[1])
            point_list.append(points[2])
            point_list.append(points[3])

            for i in range(4):
                color_list.append(COLOUR_MAP[wall.base_colour])

        self.shape_walls.append(
            arcade.create_rectangles_filled_with_colors(point_list, color_list)
        )

    def get_entity_dimensions(self, entity: Entity):
        top_left = list(entity.top_left)
        top_left[1] = SCREEN_HEIGHT - top_left[1]
        top_right = list(entity.top_right)
        top_right[1] = SCREEN_HEIGHT - top_right[1]
        bottom_left = list(entity.bottom_left)
        bottom_left[1] = SCREEN_HEIGHT - bottom_left[1]
        bottom_right = list(entity.bottom_right)
        bottom_right[1] = SCREEN_HEIGHT - bottom_right[1]
        return (top_left, top_right, bottom_right, bottom_left)

    def draw_entity(self, entity: Entity):

        left = (entity.x - entity.half_width)
        right = (entity.x + entity.half_width)
        # because arcade 0 on y is the bottom of the screen not the top
        bottom = abs((entity.y + entity.half_height) - SCREEN_HEIGHT)
        #bottom = entity.y - entity.half_height - SCREEN_HEIGHT
        top = abs((entity.y - entity.half_height) - SCREEN_HEIGHT)
        #top = entity.y + entity.half_height - SCREEN_HEIGHT

        arcade.draw_lrtb_rectangle_filled(
            left = left, 
            right = right,
            bottom = bottom, 
            top = top,
            color = COLOUR_MAP[entity.base_colour],
            )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        game = self.game

        if not game.is_running:
            return

        # Call draw() on all your sprite lists below
        self.shape_walls.draw()

        if game.game_message != "":
            arcade.draw_text(
                game.game_message,
                (SCREEN_WIDTH / 2),
                SCREEN_HEIGHT,
                arcade.color.GREEN,
                14,
                align="center",
                anchor_x="center",
                anchor_y="top",
            )

        scores = "Score: {a} - Herder Speed: {b:.2f} - Rabbit Speed: {c:.2f}".format(
            a = game.score,
            b = game.player.speed,
            c = game.rabbit.speed,
        )

        arcade.draw_text(
            scores,
            (SCREEN_WIDTH / 2),
            SCREEN_HEIGHT - 23,
            arcade.color.WHITE,
            14,
            align="center",
            anchor_x="center",
            anchor_y = "top",
        )

        draw_item_ids = False
        items = game.items.copy()
        for item in items:
            item.think(0)
            self.draw_entity(item)

        del items

        npcs = game.npcs.copy()

        for npc in npcs:
            npc.think(0)
            self.draw_entity(npc)

        del npcs

        self.draw_entity(game.player)

        draw_grid = False
        if draw_grid:
            pass
            #grid = self.game.grid
            #for point in grid.flat_pixel_positions:
            #    pyxel.pix(point[1], point[0], Colour.PINK.value)

        # Finish the render.
        # Nothing will be drawn without this.
        # Must happen after all draw commands


    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        # Call draw() on all your sprite lists below
        game = self.game
        if not game.is_running:
            return

        items = game.items.copy()
        for item in items:
            item.think(delta_time)

        del items

        npcs = game.npcs.copy()
        for npc in npcs:
            npc.think(delta_time)
        del npcs

        game.player.think(delta_time)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if not self.game.is_running:
            return

        player = self.game.player
        rabbit = self.game.rabbit

        if key == arcade.key.LEFT:
            player.set_direction(MovementDirection.WEST)
        elif key == arcade.key.RIGHT:
            player.set_direction(MovementDirection.EAST)
        elif key == arcade.key.UP:
            player.set_direction(MovementDirection.NORTH)
        elif key == arcade.key.DOWN:
            player.set_direction(MovementDirection.SOUTH)
        # debug stuffs
        elif key == arcade.key.PERIOD:
            player.tick_rate -= 1
        elif key == arcade.key.COMMA:
            player.tick_rate += 1
        elif key == arcade.key.R:
            self.game.load_level()
        elif key == arcade.key.W:
            rabbit.movement_type = MovementType.NONE
            rabbit.target = None
            rabbit.move_up()
        elif key == arcade.key.A:
            rabbit.movement_type = MovementType.NONE
            rabbit.target = None
            rabbit.move_left()
        elif key == arcade.key.D:
            rabbit.movement_type = MovementType.NONE
            rabbit.target = None
            rabbit.move_right()
        elif key == arcade.key.S:
            rabbit.movement_type = MovementType.NONE
            rabbit.target = None
            rabbit.move_down()
        elif key == arcade.key.X:
            self.game.start_rabbit()

    def on_key_release(self, key, modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        player: MovableEntity = self.game.player
        
        if key == arcade.key.LEFT:
            if player.movement_direction == MovementDirection.WEST:
                player.set_direction(MovementDirection.NONE)
        elif key == arcade.key.RIGHT:
            if player.movement_direction == MovementDirection.EAST:
                player.set_direction(MovementDirection.NONE)
        elif key == arcade.key.UP:
            if player.movement_direction == MovementDirection.NORTH:
                player.set_direction(MovementDirection.NONE)
        elif key == arcade.key.DOWN:
            if player.movement_direction == MovementDirection.SOUTH:
                player.set_direction(MovementDirection.NONE)

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Called when a user releases a mouse button.
        """
        grid_y = SCREEN_HEIGHT - y

        if button == arcade.MOUSE_BUTTON_LEFT:
            self.game.debug_x_y(x, grid_y)
            # self.game.player.move_to_point(x, grid_y)


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
