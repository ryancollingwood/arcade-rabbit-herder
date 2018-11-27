from consts import Colour


class Button:
    """ Text-based button """
    def __init__(self,
                 center_x, center_y,
                 width, height,
                 text,
                 on_press,
                 on_release,
                 font_size=18,
                 font_face="Arial",
                 face_color=Colour.LIGHT_GREY,
                 highlight_color=Colour.WHITE,
                 shadow_color=Colour.GREY,
                 button_height=2):
        
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.font_face = font_face
        self.pressed = False
        self.face_color = face_color.value
        self.highlight_color = highlight_color.value
        self.shadow_color = shadow_color.value
        self.button_height = button_height
        self._on_press = on_press
        self._on_release = on_release
        
    def on_press(self, button):
        self.pressed = True
        if self._on_press:
            self._on_press(button)

    def on_release(self, button):
        self.pressed = False
        if self._on_release:
            self._on_release(button)
