from .button import Button


class ButtonList:
    
    # expose `items` for list like operations
    def __init__(self):
        self.items = list()
        
    def __iter__(self):
        return iter(self.items)
    
    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return self.items[item]
        
    def add_button(self, button: Button):
        """
        Add a button to the button list
        :param button:
        :return:
        """
        self.items.append(button)

    def check_mouse_press_for_buttons(self, x, y):
        """
        Given an x, y, see if we need to register any button clicks.
        :param x:
        :param y:
        :return:
        """
        
        if not x:
            return
        
        if not y:
            return
        
        for button in self.items:
            if button.check_click(x, y):
                button.on_press(button)
                # this assumes only one button can be clicked for an x,y
                break

    def check_mouse_release_for_buttons(self, x, y):
        """
        If a mouse button has been released, see if we need to process any release events.
        :param x:
        :param y:
        :return:
        """
        
        for button in self.items:
            if button.pressed:
                # if it's pressed check we're still on the button
                if button.check_click(x, y):
                    button.on_release(button)
