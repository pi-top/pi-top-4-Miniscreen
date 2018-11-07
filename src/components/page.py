from components.helpers.MenuPageHelper import MenuPageHelper


class MenuPage:
    """Base view on screen"""

    def __init__(self, page_id, select_action_menu):
        """Constructor for MenuPage"""
        self.select_action_menu = select_action_menu
        self.hotspot = MenuPageHelper.get_hotspot(page_id)