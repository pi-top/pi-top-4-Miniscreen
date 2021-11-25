import logging
from dataclasses import dataclass
from typing import List

from .event import AppEvents, post_event
from .tile_group import TileGroup

logger = logging.getLogger(__name__)


@dataclass
class TileGroupContext:
    tile_groups: List[TileGroup]
    name: str = ""
    index: int = 0

    @property
    def current_tile_group(self):
        return self.tile_groups[self.index]

    def go_to_next_tile_group(self):
        logger.debug("Going to next tile group")

        self.current_tile_group.active = False
        self.index = (self.index + 1) % len(self.tile_groups)
        self.current_tile_group.active = True

    def can_go_to_next_tile_group(self):
        return len(self.tile_groups) > 1


@dataclass
class TileGroupContextManager:
    contexts: List[TileGroupContext]
    index: int = 0

    def register(self, context):
        self.contexts.append(context)

    def remove(self, context):
        if context not in self.contexts:
            return
        if self.index == self.contexts.index(context):
            self.index -= 1
        self.contexts.remove(context)

    @property
    def current_context(self):
        return self.contexts[self.index]

    @property
    def current_tile_group(self):
        return self.current_context.current_tile_group

    def switch_to(self, context_name):
        self.current_tile_group.active = False

        for index, context in enumerate(self.contexts):
            if context.name == context_name:
                self.index = index

        self.current_tile_group.active = True
        post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    def handle_cancel_button(self):
        logger.debug("Handling Cancel button press")
        if self.current_context.can_go_to_next_tile_group():
            self.current_context.go_to_next_tile_group()
        else:
            # go to main context
            self.current_tile_group.active = False
            self.index = 0
            self.current_tile_group.active = True
        post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    def handle_select_button(self):
        logger.debug("Handling Select button press")
        child_context_name = (
            self.current_tile_group.menu_tile._current_page.child_context_name
        )
        if child_context_name:
            self.switch_to(child_context_name)
        else:
            logger.debug("Handling action")
