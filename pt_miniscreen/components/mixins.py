from abc import abstractmethod
from typing import Callable


class HasGutterIcons:
    GUTTER_WIDTH = 10

    @abstractmethod
    def top_gutter_icon(self):
        pass

    @abstractmethod
    def bottom_gutter_icon(self):
        pass


class Navigable:
    @abstractmethod
    def go_next(self):
        pass

    @abstractmethod
    def go_previous(self):
        pass

    @abstractmethod
    def go_top(self):
        pass


class Poppable:
    _pop: Callable

    def set_pop(self, callback: Callable):
        self._pop = callback

    def pop(self, elements=1):
        self._pop(elements=elements)


class Enterable:
    animate_enterable_operation: bool = True

    @property
    @abstractmethod
    def enterable_component(self):
        pass


class Actionable:
    @abstractmethod
    def perform_action(self):
        pass


class BlocksMiniscreenButtons:
    @property
    @abstractmethod
    def block_buttons(self):
        pass
