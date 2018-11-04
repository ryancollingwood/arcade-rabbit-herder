# Library imports
import arcade

from game import Game
from entity import Entity, MovementType, MovementDirection
from consts.colour import Colour

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

    def setup(self):
        # Create your sprites and sprite lists here
        self.game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, 1)

    def draw_entity(self, entity: Entity):

        left = (entity.x - entity.half_width)
        right = (entity.x + entity.half_width)
        # because arcade 0 on y is the bottom of the screen not the top
        bottom = abs((entity.y + entity.half_height) - SCREEN_HEIGHT)
        top = abs((entity.y - entity.half_height) - SCREEN_HEIGHT)

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

        # Call draw() on all your sprite lists below
        game = self.game
        walls = self.game.walls

        draw_item_ids = False
        items = game.items.copy()
        for item in items:
            item.think(0)
            self.draw_entity(item)

            if draw_item_ids:
                pyxel.text(
                    item.top_left[0], 
                    item.top_left[1], 
                    str(item.id), 
                    Colour.BLACK.value
                    )
        del items

        npcs = game.npcs.copy()
        for npc in npcs:
            npc.think(0)
            self.draw_entity(npc)

        del npcs

        self.draw_entity(game.player)
            
        draw_wall_ids = False

        for wall in walls:
            self.draw_entity(wall)

            if draw_wall_ids:
                pass

        # draw scores
        # draw messages

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
        walls = self.game.walls

        draw_item_ids = False
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
        #elif key == arcade.key.LEFT_BUTTON:
        #    self.game.debug_x_y(pyxel.mouse_x, pyxel.mouse_y)
        # rabbit cheat
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
        player = self.game.player
        
        if key == arcade.key.LEFT:
            player.set_direction(MovementDirection.NONE)
        elif key == arcade.key.RIGHT:
            player.set_direction(MovementDirection.NONE)
        elif key == arcade.key.UP:
            player.set_direction(MovementDirection.NONE)
        elif key == arcade.key.DOWN:
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
        pass


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
