import logging
from dataclasses import dataclass
from typing import List

from .event import AppEvents, post_event
from .tile_group import TileGroup

logger = logging.getLogger(__name__)


@dataclass
class TileGroupContext:
    tile_groups: List[TileGroup]
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

    def _switch_to_latest(self):
        self.current_tile_group.active = False
        self.index = len(self.contexts) - 1
        self.current_tile_group.active = True
        post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    def handle_cancel_button(self):
        logger.debug("Handling Cancel button press")
        if self.current_context.can_go_to_next_tile_group():
            self.current_context.go_to_next_tile_group()
        else:
            # pop tile group context
            self.current_tile_group.active = False
            self.remove(self.current_context)
            self.current_tile_group.active = True
        post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    def handle_select_button(self):
        logger.debug("Handling Select button press")
        new_tile_group = (
            self.current_tile_group.menu_tile._current_page.child_tile_group
        )
        if new_tile_group:
            self.register(TileGroupContext(tile_groups=[new_tile_group]))
            self._switch_to_latest()
        else:
            logger.debug("Handling action")
