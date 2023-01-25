from abc import abstractmethod


class HasGutterIcons:
    @abstractmethod
    def top_gutter_icon(self, **kwargs):
        pass

    @abstractmethod
    def bottom_gutter_icon(self, **kwargs):
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


class Enterable:
    animate_enterable_operation: bool = True

    @property
    @abstractmethod
    def enterable_component(self):
        pass


class Actionable:
    @abstractmethod
    def perform_action(self, **kwargs):
        pass


class OnEnterRuns:
    @abstractmethod
    def on_enter(self, **kwargs):
        pass
