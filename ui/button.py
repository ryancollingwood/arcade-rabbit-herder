from typing import Callable
from consts import Colour


class Button:
    """
    Text-based button - adapted from http://arcade.academy/examples/gui_text_button.html#gui-text-button
    """
    
    def __init__(
            self,
            center_x: int, center_y: int,
            width: int, height: int,
            text: str,
            on_press: Callable[[object], None],
            on_release: Callable[[object], None],
            font_size: int = 18,
            font_face: str = "Arial",
            face_color: Colour = Colour.GREY,
            highlight_color: Colour = Colour.WHITE,
            shadow_color: Colour = Colour.GREY_DARK,
            button_height: int = 2
    ):
        """
        Describe a button, the rendering is not the responsibility of this class.
        
        :param center_x:
        :param center_y:
        :param width:
        :param height:
        :param text:
        :param on_press:
        :param on_release:
        :param font_size:
        :param font_face:
        :param face_color:
        :param highlight_color:
        :param shadow_color:
        :param button_height:
        """
        
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
        """
        Set the `pressed` variable `True` and call the underlying desired `_on_press` method if any
        :param button:
        :return:
        """
        
        self.pressed = True
        if self._on_press:
            self._on_press(button)

    def on_release(self, button):
        """
        Set the `pressed` variable `False` and call the underlying desired `_on_release` method if any
        :param button:
        :return:
        """

        self.pressed = False
        if self._on_release:
            self._on_release(button)

    def check_click(self, x, y):
        """
        For a given x,y pixel position does it fall within the bounds of the button?
        :param x:
        :param y:
        :return:
        """
        
        if x > self.center_x + self.width / 2:
            return False
        if x < self.center_x - self.width / 2:
            return False
        if y > self.center_y + self.height / 2:
            return False
        if y < self.center_y - self.height / 2:
            return False

        return True

