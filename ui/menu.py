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
            base_colour: Colour = Colour.DARK_GREY, ui_layout: UiLayout = UiLayout.MAIN_MENU, add_back_button: bool = True,
            button_width = 100, button_height = 30, button_padding = 5
    ):
        """
        Create a menu object. The responsibility of rendering the menu is not in this class.
        
        :param text_lines: Lines of text to be displayed
        :param is_modal: Should game execution be paused while this menu is displayed
        :param width: Pixel width of menu
        :param height: Pixel height of menu
        :param base_colour: What is the base colour of  the menu
        :param ui_layout: The positioning and number of buttons is determined by the `ui_layout`
        :param add_back_button: If `True` then a button for dismissing the menu will be added
        :param button_width: Default pixel width of buttons added to the menu
        :param button_height: Default pixel height of buttons added to the menu
        :param button_padding: Number of pixels between buttons
        """
        
        self.is_visible: bool = False
        self.width: int = width
        self.height: int = height

        # this is used for `keyboard` navigation of the menu
        self.selected_index: int = -1
        
        self.button_width = button_width
        self.button_height = button_height
        self.button_padding = button_padding
        self.base_colour = base_colour.value
        
        self.button_list: ButtonList = ButtonList()
        self.text_lines: List[str] = text_lines
        self.font_size_px = 12  # TODO: Make this accessible via constructor or some other method
        self.is_modal: bool = is_modal
        self.ui_layout = ui_layout
        
        if add_back_button:
            self.add_back_button()

    def add_back_button(self):
        """
        Add a button for dismissing (closing) the menu
        :return:
        """
        
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
        
        if self.selected_index == -1:
            self.selected_index = 0
        
    def add_button(self, button_text, on_press, on_release):
        """
        Add a button to the menu object, using the menu defaults for button properties.
        
        The ordering both in terms of the button position in the list of buttons and position on screen is not handled
        here. So you should add the buttons in order of their on screen position
        TODO: Implement some re-ordering function based on the x,y positions of buttons on some convention (left/right?)
        
        :param button_text: Text to be displayed on the button
        :param on_press: Function to be called while the button is pressed
        :param on_release: Function to called when the button is released - this is most likely where you want things
        :return:
        """
        
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
        """
        Can we close the menu? Expected to overridden in derived classes.
        :return:
        """
        
        return True
        
    def close_menu(self, button):
        """
        If `can_close` returns `True` then dismiss (close) the menu
        :param button:
        :return:
        """
        
        if self.can_close():
            self.is_visible = False

    def decrement_selected_button(self):
        """
        Decrease the selected button index, i.e. Move menu cursor up
        :return:
        """
        
        if len(self.button_list) == 0:
            self.selected_index = -1
            return

        if self.selected_index == 0:
            self.selected_index = len(self.button_list) - 1
        else:
            self.selected_index -= 1

    def increment_selected_button(self):
        """
        Increase the selected button index, i.e. Move menu cursor down
        :return:
        """
        
        if len(self.button_list) == 0:
            self.selected_index = -1
            return

        if self.selected_index == len(self.button_list) -1:
            self.selected_index = 0
        else:
            self.selected_index += 1

    def click_selected_button(self):
        """
        Emulate the click on_release action for our selected index button
        :return:
        """
        
        if self.selected_index == -1:
            return

        button = self.button_list[self.selected_index]
        if button.on_release:
            button.on_release(None)