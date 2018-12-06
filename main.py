# Library imports
import arcade

from game import Game
from entity import Entity
from shape_sprite import ShapeSprite
from ui import Menu
from consts.colour import Colour
from consts import Keys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 25

VIEW_PORT_WIDTH_MARGIN = SCREEN_WIDTH // 2
VIEW_PORT_HEIGHT_MARGIN = SCREEN_HEIGHT // 2

VIEW_PORT_SCALING = 1.5

COLOUR_MAP = {
    Colour.BLACK.value: arcade.color.BLACK,
    Colour.BLUE.value: arcade.color.BLUE,
    Colour.GREEN.value: arcade.color.GREEN,
    Colour.CYAN.value: arcade.color.CYAN,
    Colour.RED.value: arcade.color.RED,
    Colour.PURPLE.value: arcade.color.PURPLE,
    Colour.ORANGE.value: arcade.color.ORANGE,
    Colour.GREY.value: arcade.color.GRAY,
    Colour.GREY_DARK.value: arcade.color.DARK_GRAY,
    Colour.BLUE_LIGHT.value: arcade.color.LIGHT_BLUE,
    Colour.GREEN_LIGHT.value: arcade.color.LIGHT_GREEN,
    Colour.CYAN_LIGHT.value: arcade.color.LIGHT_CYAN,
    Colour.RED_LIGHT.value: arcade.color.LIGHT_RED_OCHRE,
    Colour.PURPLE_LIGHT.value: arcade.color.LIGHT_PASTEL_PURPLE,
    Colour.YELLOW.value: arcade.color.YELLOW,
    Colour.WHITE.value: arcade.color.WHITE,
    Colour.BROWN.value: arcade.color.BROWN,
}

KEY_MAP = {
    arcade.key.UP: Keys.UP,
    arcade.key.DOWN: Keys.DOWN,
    arcade.key.LEFT: Keys.LEFT,
    arcade.key.RIGHT: Keys.RIGHT,

    arcade.key.SPACE: Keys.SPACE,
    arcade.key.ESCAPE: Keys.ESCAPE,
    arcade.key.RETURN: Keys.RETURN,

    arcade.key.W: Keys.W,
    arcade.key.S: Keys.S,
    arcade.key.A: Keys.A,
    arcade.key.D: Keys.D,

    arcade.key.R: Keys.R,
    arcade.key.X: Keys.X,
    arcade.key.COMMA: Keys.COMMA,
    arcade.key.PERIOD: Keys.PERIOD,
}


class MyGame(arcade.Window):
    
    def __init__(self, width, height):
        self.debug = False
        super().__init__(width, height)
        self.set_update_rate(1 / 20)
        
        arcade.set_background_color(arcade.color.BLACK)
        
        self.game = None
        self.last_level = None
        # If you have sprite lists, you should create them here,
        # and set them to None
        self.shape_walls = None
        self.entities_shapelist = dict()
        
        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left: int = 0
        self.view_bottom: int = 0
    
    def setup(self):
        """
        Setup shapes and sprites (if we had any) and initialise the game class
        :return:
        """
        # Create your sprites and sprite lists here
        self.game: Game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, 1, grid_layers = 4)
        self.game.game_message = "Lead the Rabbit home"

        # show the menu so that we see the instructions
        self.game.menu.button_list[0].text = "Start"
        self.game.menu.is_visible = True
        
    def reset_level(self):
        """
        
        :return:
        """
        if self.shape_walls is not None:
            del self.shape_walls
        
        if self.entities_shapelist is not None:
            del self.entities_shapelist
        
        self.entities_shapelist = dict()
        
        self.game.load_level()

        self.create_wall_shape()
    
    def create_wall_shape(self):
        """
        Instead of rendering each wall block, we create a single shape which can be drawn in a single call,
        rather than a call for each wall block
        :return:
        """
        self.shape_walls = arcade.ShapeElementList()
        self.shape_walls.center_x = 0
        self.shape_walls.center_y = 0
        self.shape_walls.angle = 0

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
            
            # as we have 4 points
            for i in range(4):
                color_list.append(COLOUR_MAP[wall.base_colour])
        
        self.shape_walls.append(
            arcade.create_rectangles_filled_with_colors(point_list, color_list)
        )
    
    def get_entity_dimensions(self, entity: Entity):
        """
        Remap the co-ordinates from the grid to positions required by aracade.
        As 0,0 is the bottom left position in arcade, but the grid see's 0,0 as top left
        
        :param entity:
        :return:
        """
        top_left = list(entity.top_left)
        top_left[1] = SCREEN_HEIGHT - top_left[1]
        top_right = list(entity.top_right)
        top_right[1] = SCREEN_HEIGHT - top_right[1]
        bottom_left = list(entity.bottom_left)
        bottom_left[1] = SCREEN_HEIGHT - bottom_left[1]
        bottom_right = list(entity.bottom_right)
        bottom_right[1] = SCREEN_HEIGHT - bottom_right[1]
        return top_left, top_right, bottom_right, bottom_left
    
    def update_shape_sprite(self, entity: Entity):
        """
        Create/Update the sprite shape for an entity and add/update the entry for it in `self.entities_shapelist`
        :param entity:
        :return:
        """
        
        shape_sprite: ShapeSprite = entity.shape_sprite
        
        if entity.id not in self.entities_shapelist:
            entity_shapelist = arcade.ShapeElementList()
            
            # we need to convert from general colours to arcade specific colours
            entity_shapelist.append(arcade.create_rectangles_filled_with_colors(
                shape_sprite.point_list, [COLOUR_MAP[x] for x in shape_sprite.color_list])
            )
        else:
            entity_shapelist = self.entities_shapelist[entity.id]

        entity_shapelist.center_x = shape_sprite.position_x
        entity_shapelist.center_y = SCREEN_HEIGHT - shape_sprite.position_y
        entity_shapelist.draw()
        
        self.entities_shapelist[entity.id] = entity_shapelist
        
    def update_screen_boundary(self, focus_entity):
        """
        Given an area we want to focus on i.e. the player bounding box, do we need to scroll the viewport?
        
        Adapted from http://arcade.academy/examples/sprite_move_scrolling.html#sprite-move-scrolling
        :param focus_top:
        :param focus_right:
        :param focus_bottom:
        :param focus_left:
        :return:
        """

        top_left, top_right, bottom_right, bottom_left = self.get_entity_dimensions(focus_entity)

        focus_top = top_left[1]
        focus_right = top_right[0]
        focus_bottom = bottom_right[1]
        focus_left = bottom_left[0]

        # --- Manage Scrolling ---
        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEW_PORT_WIDTH_MARGIN
        if focus_left < left_bndry:
            self.view_left -= left_bndry - focus_left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEW_PORT_WIDTH_MARGIN
        if focus_right > right_bndry:
            self.view_left += focus_right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEW_PORT_HEIGHT_MARGIN
        if focus_top > top_bndry:
            self.view_bottom += focus_top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEW_PORT_HEIGHT_MARGIN
        if focus_bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - focus_bottom
            changed = True

        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)
            
    def draw_entity(self, entity: Entity):
        """
        Draw the entity as a block, converting the y pixels values for 0,0 being bottom left not top left
        :param entity:
        :return:
        """
        
        if entity.shape_sprite:
            return self.update_shape_sprite(entity)
        
        left = (entity.x - entity.half_width)
        right = (entity.x + entity.half_width)
        # because arcade 0 on y is the bottom of the screen not the top
        bottom = abs((entity.y + entity.half_height) - SCREEN_HEIGHT)
        # bottom = entity.y - entity.half_height - SCREEN_HEIGHT
        top = abs((entity.y - entity.half_height) - SCREEN_HEIGHT)
        # top = entity.y + entity.half_height - SCREEN_HEIGHT
        
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
        game = self.game
        
        if not game.is_running:
            return

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()
        
        # Call draw() on all your sprite lists below

        # have the walls changed?
        self.shape_walls.draw()

        if game.rabbit.path:
            self.draw_path(game.rabbit.path)

        if game.game_message != "":
            arcade.draw_text(
                game.game_message,
                (SCREEN_WIDTH / 2),
                SCREEN_HEIGHT,
                arcade.color.GREEN,
                14,
                align = "center",
                anchor_x = "center",
                anchor_y = "top",
            )

        try:
            scores = "Score: {a} - Held Carrots: {b}".format(
                a = game.score,
                b = game.held_carrots,
            )
        except AttributeError:
            pass
        
        arcade.draw_text(
            scores,
            (SCREEN_WIDTH / 2),
            SCREEN_HEIGHT - 23,
            arcade.color.WHITE,
            14,
            align = "center",
            anchor_x = "center",
            anchor_y = "top",
        )
        
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

        # draw menus last so they appear on top of things
        self.draw_menu()
        
        # Finish the render.
        # Nothing will be drawn without this.
        # Must happen after all draw commands
    
    def draw_path(self, path):
        """
        Draw a path for visual debugging
        :param path:
        :return:
        """
        for path_point in path:
            arcade.draw_lrtb_rectangle_filled(
                left = path_point[0] - 3,
                right = path_point[0] + 3,
                bottom = abs(path_point[1] + 3 - SCREEN_HEIGHT),
                top = abs(path_point[1] - 3 - SCREEN_HEIGHT),
                color = COLOUR_MAP[Colour.YELLOW.value],
            )
    
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

        # if level has changed redraw walls
        if self.game.level != self.last_level:
            self.reset_level()
            self.last_level = self.game.level

        if not game.update_game(delta_time):
            return
        
        player: Entity = game.player
        
        self.update_screen_boundary(player)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if not self.game.is_running:
            return

        if key == arcade.key.R:
            self.reset_level()

        try:
            game_key = KEY_MAP[key]
        except KeyError:
            return

        self.game.on_key_press(game_key)

    def on_key_release(self, key, modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        :param key:
        :param modifiers:
        :return:
        """

        try:
            game_key = KEY_MAP[key]
        except KeyError:
            return

        self.game.on_key_release(game_key)

    def get_menu_for_display(self):
        """
        Get the current menu (if any) for display
        :return:
        """
        
        game = self.game
        if not game.menu:
            return

        menu = game.menu
        if not menu.is_visible:
            return None
        
        return menu
        
    def draw_menu(self):
        """
        If the menu should be visible, then draw it
        :return:
        """
        
        menu = self.get_menu_for_display()
        if not menu:
            return

        menu_center_x, menu_center_y, menu_cords = self.get_menu_coords(menu)


        arcade.draw_rectangle_filled(
            menu_center_x, menu_center_y,
            menu.width, menu.height,
            COLOUR_MAP[menu.base_colour]
        )
        
        text_height = menu_cords[0][1] - (menu.button_padding * 3)

        for text in menu.text_lines:
            arcade.draw_text(
                text,
                menu_center_x,
                text_height,
                arcade.color.BLACK,
                12,
                align = "center",
                anchor_x = "center",
                anchor_y = "top",
            )

            text_height = text_height - (menu.button_padding * 3)
        
        for button_index, button in enumerate(menu.button_list):
            self.draw_button(
                button, menu_cords[0][0], menu_cords[0][1],
                menu.width, menu.height,
                menu.selected_index == button_index
            )

    def get_menu_coords(self, menu):
        """
        Get the pixel positions for positioning a menu in the center of the screen
        :param menu:
        :return:
        """
        
        menu_center_x = (self.width // 2) + self.view_left
        menu_center_y = (self.height // 2) + self.view_bottom
        # get a mapping of the menu co-ordinates for relative positioning of things inside the menu
        menu_cords = (
            (menu_center_x - (menu.width // 2), menu_center_y + (menu.height // 2)),
            (menu_center_x + (menu.width // 2), menu_center_y + (menu.height // 2)),
            (menu_center_x - (menu.width // 2), menu_center_y - (menu.height // 2)),
            (menu_center_x + (menu.width // 2), menu_center_y - (menu.height // 2)),
        )
        return menu_center_x, menu_center_y, menu_cords

    def draw_button(self, button, relative_x, relative_y, menu_width, menu_height, is_selected):
        """
        Draw a square for the button. If button is selected display an indicator (e.g. yellow triangle) next to it
        :param button:
        :param relative_x:
        :param relative_y:
        :param menu_width:
        :param menu_height:
        :param is_selected:
        :return:
        """
        
        # adapted from http://arcade.academy/examples/gui_text_button.html#gui-text-button
        screen_button_center_x = (SCREEN_WIDTH - button.center_x - relative_x) + self.view_left
        screen_button_center_y = (menu_height + SCREEN_HEIGHT - button.center_y - relative_y) + self.view_bottom

        arcade.draw_rectangle_filled(
            screen_button_center_x,
            screen_button_center_y,
            button.width, button.height,
            COLOUR_MAP[button.face_color]
        )

        if is_selected:
            selected_x = screen_button_center_x - (button.width // 2) - 25
            selector_height = 10
            selector_width = 16
            arcade.draw_triangle_filled(
                selected_x, screen_button_center_y - selector_height,
                selected_x, screen_button_center_y + selector_height,
                selected_x + selector_width, screen_button_center_y,
                COLOUR_MAP[Colour.YELLOW.value]
            )

        if not button.pressed:
            color = COLOUR_MAP[button.shadow_color]
        else:
            color = COLOUR_MAP[button.highlight_color]

        # Bottom horizontal
        arcade.draw_line(screen_button_center_x - button.width / 2, screen_button_center_y - button.height / 2,
                         screen_button_center_x + button.width / 2, screen_button_center_y - button.height / 2,
                         color, button.button_height)

        # Right vertical
        arcade.draw_line(screen_button_center_x + button.width / 2, screen_button_center_y - button.height / 2,
                         screen_button_center_x + button.width / 2, screen_button_center_y + button.height / 2,
                         color, button.button_height)

        if not button.pressed:
            color = COLOUR_MAP[button.highlight_color]
        else:
            color = COLOUR_MAP[button.shadow_color]

        # Top horizontal
        arcade.draw_line(screen_button_center_x - button.width / 2, screen_button_center_y + button.height / 2,
                         screen_button_center_x + button.width / 2, screen_button_center_y + button.height / 2,
                         color, button.button_height)

        # Left vertical
        arcade.draw_line(screen_button_center_x - button.width / 2, screen_button_center_y - button.height / 2,
                         screen_button_center_x - button.width / 2, screen_button_center_y + button.height / 2,
                         color, button.button_height)

        x = screen_button_center_x
        y = screen_button_center_y
        if not button.pressed:
            x -= button.button_height
            y += button.button_height

        arcade.draw_text(button.text, x, y,
                         arcade.color.BLACK, font_size=button.font_size,
                         width=button.width, align="center",
                         anchor_x="center", anchor_y="center")
        
    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        
        pass
    
    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        
        menu: Menu = self.get_menu_for_display()

        menu_click_x, menu_click_y = self.get_menu_click(menu, x, y)

        if button == arcade.MOUSE_BUTTON_LEFT:
            if menu:
                menu.button_list.check_mouse_press_for_buttons(
                    menu_click_x,
                    menu_click_y,
                )

    def get_menu_click(self, menu, x, y):
        """
        Translate to the arcade screen pixel position to co-ordinate values relative to the menu.
        Used for determining if a button has been clicked.
        :param menu:
        :param x:
        :param y:
        :return:
        """
        
        menu_click_x = None
        menu_click_y = None

        if menu:
            menu_center_x, menu_center_y, menu_cords = self.get_menu_coords(menu)
            
            menu_click_x = menu.width - (SCREEN_WIDTH - x - menu_cords[0][0])
            menu_click_y = menu.height + (SCREEN_HEIGHT - y - menu_cords[0][1])

            # Transform the values for out of bounds values
            if menu_click_x > menu.width or menu_click_x < 0:
                menu_click_x = None

            if menu_click_y > menu.height or menu_click_y < 0:
                menu_click_y = None

        return menu_click_x, menu_click_y

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Called when a user releases a mouse button.
        :param x:
        :param y:
        :param button:
        :param modifiers:
        :return:
        """
        
        menu: Menu = self.get_menu_for_display()

        menu_click_x, menu_click_y = self.get_menu_click(menu, x, y)

        if button == arcade.MOUSE_BUTTON_LEFT:
            if menu:
                menu.button_list.check_mouse_release_for_buttons(
                    menu_click_x,
                    menu_click_y,
                )
    
    # from here below are inherited methods in which we are just calling the super class's method
    def _create(self):
        return super()._create()
    
    def _recreate(self, changes):
        return super()._recreate(changes)
    
    def flip(self):
        return super().flip()
    
    def switch_to(self):
        return super().switch_to()
    
    def set_caption(self, caption):
        return super().set_caption(caption)
    
    def set_minimum_size(self, width, height):
        return super().set_minimum_size(width, height)
    
    def set_maximum_size(self, width, height):
        return super().set_maximum_size(width, height)
    
    def set_location(self, x, y):
        return super().set_location(x, y)
    
    def activate(self):
        return super().activate()
    
    def minimize(self):
        return super().minimize()
    
    def maximize(self):
        return super().maximize()
    
    def set_vsync(self, vsync):
        return super().set_vsync(vsync)
    
    def set_mouse_platform_visible(self, platform_visible = None):
        return super().set_mouse_platform_visible(platform_visible)
    
    def set_exclusive_mouse(self, exclusive = True):
        return super().set_exclusive_mouse(exclusive)
    
    def set_exclusive_keyboard(self, exclusive = True):
        return super().set_exclusive_keyboard(exclusive)
    
    def get_system_mouse_cursor(self, name):
        return super().get_system_mouse_cursor(name)
    
    def dispatch_events(self):
        return super().dispatch_events()


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()

