from .button import Button


class ButtonList:
    def __init__(self):
        self.items = list()
        
    def __iter__(self):
        return iter(self.items)
        
    def add_button(self, button: Button):
        self.items.append(button)

    def check_mouse_press_for_buttons(self, x, y):
        """ Given an x, y, see if we need to register any button clicks. """
        for button in self.items:
            if x > button.center_x + button.width / 2:
                continue
            if x < button.center_x - button.width / 2:
                continue
            if y > button.center_y + button.height / 2:
                continue
            if y < button.center_y - button.height / 2:
                continue
            button.on_press(button)

    def check_mouse_release_for_buttons(self, x, y):
        """ If a mouse button has been released, see if we need to process
            any release events. """
        for button in self.items:
            if button.pressed:
                button.on_release(button)

