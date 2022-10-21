from enum import Enum, auto
from typing import Dict


class Message(Enum):
    PUB_PITOPD_READY = auto()


class PTDMSubscribeClient:
    subs: Dict = {}

    def initialise(self, message_to_func_dict: Dict) -> None:
        self.subs.update(message_to_func_dict)

    def start_listening(self) -> None:
        pass

    def stop_listening(self) -> None:
        pass
