from typing import List
from .button import Button
from .button_list import ButtonList
from consts import UiLayout
from consts import Colour


class Menu:
    def __init__(
            self,
            text_lines: List[str], is_modal: bool, width: int, height: int,
            base_colour: Colour = Colour.DARK_GREY, ui_layout: UiLayout = UiLayout.MAIN_MENU, add_close_button: bool = True,
            button_width = 100, button_height = 30, button_padding = 5
    ):
        self.is_visible: bool = False
        self.selected_index: int = -1
        self.width: int = width
        self.height: int = height
        
        self.button_width = button_width
        self.button_height = button_height
        self.button_padding = button_padding
        self.base_colour = base_colour.value
        
        self.button_list: ButtonList = ButtonList()
        self.text_lines: List[str] = text_lines
        self.is_modal: bool = is_modal
        self.ui_layout = ui_layout
        
        if add_close_button:
            self.add_close_button()

    def add_close_button(self):
        button_text = "Back"
        button_height = self.button_height
        button_width = self.button_width
        
        if self.ui_layout == UiLayout.MAIN_MENU:
            button_x = self.width // 2
            button_y = self.height - self.button_padding - (button_height // 2)
        else:
            button_x = self.button_width - self.button_padding - (button_width // 2)
            button_y = self.height - self.button_padding - (button_height // 2)
            button_text = "X"

        self.button_list.add_button(Button(
            center_x = button_x, center_y = button_y,
            width = button_width, height = button_height,
            text = button_text,
            on_press = None,
            on_release = self.close_menu,
        ))
        
    def can_close(self):
        return True
        
    def close_menu(self, button):
        if self.can_close():
            self.is_visible = False
