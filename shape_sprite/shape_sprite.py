import arcade


class ShapeSprite:
    # TODO: Move all arcade specific stuff out of this
    
    def __init__(self, name, position_x, position_y, square_size):
        """
        Create an object describing a sprite that is a shape consisting of multiple blocks
        
        :param name:
        :param position_x:
        :param position_y:
        :param square_size:
        """
        
        self.name = name
        self.position_x = position_x
        self.position_y = position_y
        self.shape_list = None
        self.square_size = square_size
        
        self.width = 0
        self.half_width = 0
        self.height = 0
        self.half_height = 0
        
        self.point_list = None
        self.color_list = None
        
        with open(f"resources\shape_sprite\{name}\shape.txt") as f:
            self.lines = f.readlines()

        self.create_shape_list()
    
    def create_shape_list(self):
        self.shape_list = arcade.ShapeElementList()
        
        point_list = []
        color_list = []
        
        """
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
        """
        
        self.height = self.square_size * len(self.lines)
        
        # we build the shape_sprite in reverse for the benefit of arcade
        # TODO: this might need to be a configurable variable
        for line_index, line_value in enumerate(reversed(self.lines)):
            column_values = line_value.split("\t")  # at the moment the text files are tab delimited
            
            line_width = len(column_values) * self.square_size
            if line_width > self.width:
                self.width = line_width
                
            for column_index, value in enumerate(column_values):
                
                try:
                    value = int(value)
                except ValueError:
                    continue
                
                top_left = (column_index * self.square_size, line_index * self.square_size)
                top_right = (top_left[0] + self.square_size, top_left[1])
                bottom_right = (top_left[0] + self.square_size, top_left[1] + self.square_size)
                bottom_left = (top_left[0], top_left[1] + self.square_size)
                
                point_list.append(top_left)
                point_list.append(top_right)
                point_list.append(bottom_right)
                point_list.append(bottom_left)
                
                colour = value
                
                for i in range(4):
                    color_list.append(colour)
        
        self.half_width = self.width // 2
        self.half_height = self.height // 2
        
        self.point_list = point_list
        self.color_list = color_list
        
    def update(self, x, y):
        """
        Update the position, being the centre of the shape for a given x,y pixel position
        
        :param x:
        :param y:
        :return:
        """
        
        self.position_x = x - self.half_width
        self.position_y = y + self.half_height
