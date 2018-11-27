import arcade

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

HALF_SQUARE_WIDTH = 2.5
HALF_SQUARE_HEIGHT = 2.5
SQUARE_SPACING = 10


class ShapeSprite:
    def __init__(self, position_x, position_y, square_size, lines):

        # Take the parameters of the init function above, and create instance variables out of them.
        self.position_x = position_x
        self.position_y = position_y
        self.shape_list = None
        self.square_size = square_size
        
        self.lines = lines
        self.create_shape_list()
        
    def create_shape_list(self):
        self.shape_list = arcade.ShapeElementList()
        
        point_list = []
        color_list = []
        
        colour_codes = [
            arcade.color.BLACK,  # 0
            arcade.color.BLUE,  # 1
            arcade.color.GREEN,  # 2
            arcade.color.CYAN,  # 3
            arcade.color.RED,  # 4
            arcade.color.MAGENTA,  # 5
            arcade.color.BROWN,  # 6
            arcade.color.LIGHT_GRAY,  # 7
            arcade.color.DARK_GRAY,  # 8
            arcade.color.LIGHT_BLUE,  # 9
            arcade.color.LIGHT_GREEN,  # 10
            arcade.color.LIGHT_CYAN,  # 11
            arcade.color.LIGHT_RED_OCHRE,  # 12
            arcade.color.LIGHT_MEDIUM_ORCHID,  # 13
            arcade.color.WHITE
        ]
        
        for row_index, row_value in enumerate(reversed(self.lines)):
            for column_index, value in enumerate(row_value):
                
                try:
                    value = int(value)
                except ValueError:
                    continue
                
                top_left = (column_index * self.square_size, row_index * self.square_size)
                top_right = (top_left[0] + self.square_size, top_left[1])
                bottom_right = (top_left[0] + self.square_size, top_left[1] + self.square_size)
                bottom_left = (top_left[0], top_left[1] + self.square_size)

                point_list.append(top_left)
                point_list.append(top_right)
                point_list.append(bottom_right)
                point_list.append(bottom_left)
                
                colour = colour_codes[value]

                for i in range(4):
                    color_list.append(colour)
        
        self.shape_list.append(
            arcade.create_rectangles_filled_with_colors(point_list, color_list)
        )


    def draw(self):
        """ Draw the balls with the instance variables we have. """
        self.shape_list.center_x = self.position_x
        self.shape_list.center_y = self.position_y
        self.shape_list.draw()


class MyGame(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.ASH_GREY)

        self.odds = True

        # Create our shape_sprite
        self.shape_sprite = ShapeSprite(50, 50, 7, [
            ",14, 14, 14,, 14, 14, 14,".split(","),
            ", 14, 13, 14,, 14, 13, 14,".split(","),
            ", 14, 13, 14,, 14, 13, 14,".split(","),
            ", 14, 13, 14,, 14, 13, 14,".split(","),
            ", 14, 14, 14, 14, 14, 14, 14,".split(","),
            "14, 7, 3, 1, 7, 3, 1, 14, 14".split(","),
            "14, 14, 3, 3, 14, 3, 3, 14, 14".split(","),
            "14, 14, 14, 14, 0, 14, 14, 14, 14".split(","),
            ", 14, 14, 8, 5, 8, 14, 14,".split(","),
            ", , , 14, 14, 14,, ,".split(",")
        ])
        self.shape_list = None

    def zoom_shape_sprite(self, zoom_value):
        if self.shape_sprite.square_size + zoom_value > 1:
            self.shape_sprite.square_size += zoom_value
            self.shape_sprite.create_shape_list()

    def rotate_shape_sprite(self, angle_modifier):
        self.shape_sprite.shape_list.angle += angle_modifier

    def toggle_squares(self):
        self.odds = not self.odds
        self.make_shapes()

    def make_shapes(self):
        odds = self.odds
    
        self.shape_list = arcade.ShapeElementList()
    
        # --- Create all the rectangles
    
        # We need a list of all the points and colors
        point_list = []
        color_list = []
    
        skip_x = odds
        skip_y = not odds
    
        # Now calculate all the points
        for x in range(0, SCREEN_WIDTH, SQUARE_SPACING):
        
            skip_x = not skip_x
            if skip_x:
                continue
        
            for y in range(0, SCREEN_HEIGHT, SQUARE_SPACING):
            
                skip_y = not skip_y
                if skip_y:
                    continue
            
                # Calculate where the four points of the rectangle will be if
                # x and y are the center
                top_left = (x - HALF_SQUARE_WIDTH, y + HALF_SQUARE_HEIGHT)
                top_right = (x + HALF_SQUARE_WIDTH, y + HALF_SQUARE_HEIGHT)
                bottom_right = (x + HALF_SQUARE_WIDTH, y - HALF_SQUARE_HEIGHT)
                bottom_left = (x - HALF_SQUARE_WIDTH, y - HALF_SQUARE_HEIGHT)
            
                # Add the points to the points list.
                # ORDER MATTERS!
                # Rotate around the rectangle, don't append points caty-corner
                point_list.append(top_left)
                point_list.append(top_right)
                point_list.append(bottom_right)
                point_list.append(bottom_left)
            
                # Add a color for each point. Can be different colors if you want
                # gradients.
                for i in range(4):
                    color_list.append(arcade.color.DARK_BLUE)
    
        shape = arcade.create_rectangles_filled_with_colors(point_list, color_list)
        self.shape_list.append(shape)

    def setup(self):
        self.make_shapes()

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()
        self.shape_list.draw()
        self.shape_sprite.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called to update our objects. Happens approximately 60 times per second."""
        self.shape_sprite.position_x = x
        self.shape_sprite.position_y = y
        
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.zoom_shape_sprite(scroll_y)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        print(f"You clicked button number: {button}")
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.rotate_shape_sprite(1)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.rotate_shape_sprite(-1)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.rotate_shape_sprite(1)
        elif symbol == arcade.key.LEFT:
            self.rotate_shape_sprite(-1)

    def on_mouse_release(self, x, y, button, modifiers):
        self.toggle_squares()

    def on_key_release(self, symbol: int, modifiers: int):
        self.toggle_squares()

def main():
    window = MyGame(640, 480, "Drawing Example")
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()