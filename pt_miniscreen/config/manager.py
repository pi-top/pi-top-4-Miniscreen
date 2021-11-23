import logging

from .config import app_config
from .factory import ConfigFactory

logger = logging.getLogger(__name__)


class MenuTileConfigManager:
    @staticmethod
    def get_menus_dict(size, mode):
        menus = dict()
        menu_factory = ConfigFactory(size, mode)
        for menu_name, config in app_config.children.items():
            menus[menu_name] = menu_factory.get(config)
        return menus

    @staticmethod
    def get_next_menu_id(menus, current_menu_id):
        menu_config_id_fields = current_menu_id.split(".")
        if len(menu_config_id_fields) == 1:
            # we're at a top level menu - filter out children
            keys = [
                key
                for key in menus
                if not (current_menu_id in key and current_menu_id != key)
            ]
        else:
            # we're in a node - filter out non-related menus
            lookup = ".".join(menu_config_id_fields[:-1])
            keys = [key for key in menus if (lookup in key and lookup != key)]

        candidate_menus = {key: menus[key] for key in keys}
        current_index = keys.index(current_menu_id)
        next_index = (
            0 if current_index + 1 >= len(candidate_menus) else current_index + 1
        )
        return keys[next_index]

    @staticmethod
    def get_parent_menu_id(current_menu_id):
        menu_config_id_fields = current_menu_id.split(".")

        if len(menu_config_id_fields) == 1:
            # already at parent
            return current_menu_id

        return ".".join(menu_config_id_fields[:-1])

    @staticmethod
    def menu_id_has_parent(menus, menu_id):
        menu_config_id_fields = menu_id.split(".")

        # Only one field means there's no parent
        if len(menu_config_id_fields) == 1:
            return False

        lookup = ".".join(menu_config_id_fields[:-1])

        keys = [key for key in menus if (lookup in key and lookup != key)]

        return len(keys) > 0

    @staticmethod
    def get_title_bar(size):
        if not app_config.title_bar:
            return

        return app_config.title_bar.page_cls(
            size=(size[0], app_config.title_bar.behaviour.height),
            behaviour=app_config.title_bar.behaviour,
        )
