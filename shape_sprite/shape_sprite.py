import arcade
from warnings import warn

class ShapeSprite:
    # TODO: Move all arcade specific stuff out of this
    
    def __init__(self, name, position_x, position_y, square_size):
        """
        Create an object describing a sprite that is a shape consisting of multiple blocks
        
        :param name: The directory in which the `shape.txt` is located
        :param position_x: What is the x position we will draw the shape
        :param position_y: What is the y position we will draw the shape
        :param square_size: What is the size of each block in px
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
        
        with open(f"resources/shape_sprite/{name}/shape.txt") as f:
            self.lines = f.readlines()

        self.create_shape_list()
        # now that we have `width` and `height` as determined in `create_shape_list` reposition the center
        self.update(position_x, position_y)
    
    def create_shape_list(self):
        """
        Read the `shape.txt` and build the point and colour lists we will use to create a shapelist for rendering
        
        :return:
        """
        self.shape_list = arcade.ShapeElementList()
        
        point_list = []
        color_list = []
        
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
                    # we'll not warn about empty values as that is transparency
                    if value.strip() != '':
                        warn(f"Excepted a integer, found '{value}' instead when loading ShapeSprite: {self.name}")
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
