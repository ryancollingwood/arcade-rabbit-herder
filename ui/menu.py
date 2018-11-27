from typing import List
from warnings import warn
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
        self.font_size_px = 12
        self.is_modal: bool = is_modal
        self.ui_layout = ui_layout
        
        if add_close_button:
            self.add_close_button()
            self.selected_index = 0

    def add_close_button(self):
        button_text = "Back"
        button_height = self.button_height
        button_width = self.button_width
        
        if self.ui_layout == UiLayout.MAIN_MENU:
            button_x = self.width // 2
            button_y = self.height - ((button_height + self.button_padding) // 2)
        elif self.ui_layout == UiLayout.TEXT_ONLY:
            button_x = self.button_width - self.button_padding - (button_width // 2)
            button_y = self.height - ((button_height + self.button_padding)// 2)
            button_text = "X"

        self.button_list.add_button(Button(
            center_x = button_x, center_y = button_y,
            width = button_width, height = button_height,
            text = button_text,
            on_press = None,
            on_release = self.close_menu,
        ))
        
    def add_button(self, button_text, on_press, on_release):
        button_height = self.button_height
        button_width = self.button_width
        button_padding = self.button_padding

        start_y = len(self.text_lines) * (self.font_size_px + button_padding)
        current_button_y = len(self.button_list) * (button_height + button_padding)
        
        start_y += current_button_y

        if self.ui_layout == UiLayout.MAIN_MENU:
            button_x = self.width // 2
            button_y = start_y + ((button_height + button_padding) // 2)
        elif self.ui_layout == UiLayout.TEXT_ONLY:
            warn("Tried to add button to UiLayout.TEXT_ONLY")
            return
        
        self.button_list.add_button(Button(
            center_x = button_x, center_y = button_y,
            width = button_width, height = button_height,
            text = button_text,
            on_press = on_press,
            on_release = on_release,
        ))
        
    def can_close(self):
        return True
        
    def close_menu(self, button):
        if self.can_close():
            self.is_visible = False

    def decrement_selected(self):
        if len(self.button_list) == 0:
            self.selected_index = -1
            return

        if self.selected_index == 0:
            self.selected_index = len(self.button_list) - 1
        else:
            self.selected_index -= 1

    def increment_selected(self):
        if len(self.button_list) == 0:
            self.selected_index = -1
            return

        if self.selected_index == len(self.button_list) -1:
            self.selected_index = 0
        else:
            self.selected_index += 1

    def click_selected(self):
        if self.selected_index == -1:
            return

        button = self.button_list[self.selected_index]
        if button.on_release:
            button.on_release(None)