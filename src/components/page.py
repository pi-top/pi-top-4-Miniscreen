from components.helpers import MenuHelper


class MenuPage:
    """Base view on screen"""

    def __init__(self, name, hotspot, select_action_func):
        """Constructor for MenuPage"""
        self.select_action_func = select_action_func
        self.hotspot = hotspot
        self.name = name