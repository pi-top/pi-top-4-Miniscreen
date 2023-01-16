from abc import abstractmethod
from time import sleep
from typing import Callable, Optional

from pt_miniscreen.core.components.stack import Stack
from pt_miniscreen.utils import ButtonEvents


class HasGutterIcons:
    @abstractmethod
    def top_gutter_icon(self, **kwargs):
        pass

    @abstractmethod
    def bottom_gutter_icon(self, **kwargs):
        pass


class HandlesButtonEvents:
    @abstractmethod
    def handle_button(
        self, button_event: ButtonEvents, callback: Optional[Callable], **kwargs
    ) -> None:
        pass


class Enterable:
    animate_enterable_operation: bool = True

    @property
    @abstractmethod
    def enterable_component(self):
        pass

    def enter(self, stack: Stack, on_enter: Optional[Callable]) -> None:
        if self.enterable_component is None:
            return

        stack.push(self.enterable_component, animate=self.animate_enterable_operation)

        if callable(on_enter):
            on_enter()

    def exit(self, stack: Stack, on_exit: Optional[Callable]) -> None:
        if len(stack.stack) == 1:
            return

        stack.pop(animate=self.animate_enterable_operation)
        while stack.is_popping:
            sleep(0.1)

        if callable(on_exit):
            on_exit()


class Actionable:
    @abstractmethod
    def perform_action(self, **kwargs):
        pass
