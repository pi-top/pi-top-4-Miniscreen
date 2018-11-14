import pygame  # Conditional...
from enum import Enum
from ptcommon.logger import PTLogger
from ptcommon.ptdm_message import Message
from threading import Thread
from time import sleep
import traceback
import zmq


# Creates a client for publish messages from device manager
# Listens for button presses
class RequestClient:
    _thread = Thread()

    def __init__(self):
        self._thread = Thread(target=self._thread_method)
        self._callback_client = None
        self._zmq_context = zmq.Context()
        self._zmq_socket = self._zmq_context.socket(zmq.SUB)
        self._zmq_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self._continue = False

    def initialise(self, callback_client):
        self._callback_client = callback_client

    def start_listening(self):
        PTLogger.debug("Opening request socket...")

        try:
            self._zmq_socket.connect("tcp://127.0.0.1:3781")
            PTLogger.info("Responder server ready.")

        except zmq.error.ZMQError as e:
            PTLogger.error("Error starting the request server: " + str(e))
            PTLogger.info(traceback.format_exc())

            return False

        sleep(0.5)

        self._continue = True
        self._thread.start()

        return True

    def stop_listening(self):
        PTLogger.info("Closing responder socket...")

        self._continue = False
        if self._thread.is_alive():
            self._thread.join()

        self._zmq_socket.close()
        self._zmq_context.destroy()

        PTLogger.debug("Closed responder socket.")

    def _thread_method(self):
        PTLogger.info("Listening for requests...")

        while self._continue:
            poller = zmq.Poller()
            poller.register(self._zmq_socket, zmq.POLLIN)

            events = poller.poll(500)

            for i in range(len(events)):
                message_string = self._zmq_socket.recv_string()
                message = Message.from_string(message_string)

                if message.message_id() == Message.PUB_V3_BUTTON_UP_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(ButtonPress(ButtonPress.ButtonType.UP))

                elif message.message_id() == Message.PUB_V3_BUTTON_DOWN_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(ButtonPress(ButtonPress.ButtonType.DOWN))

                elif message.message_id() == Message.PUB_V3_BUTTON_SELECT_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(ButtonPress(ButtonPress.ButtonType.SELECT))

                elif message.message_id() == Message.PUB_V3_BUTTON_CANCEL_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(ButtonPress(ButtonPress.ButtonType.CANCEL))


class ButtonPressHelper:
    @staticmethod
    def init():
        pygame.init()

    @staticmethod
    def get():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    return ButtonPress(ButtonPress.ButtonType.DOWN)
                elif event.key == pygame.K_q:
                    return ButtonPress(ButtonPress.ButtonType.UP)
                elif event.key == pygame.K_p:
                    return ButtonPress(ButtonPress.ButtonType.SELECT)
                elif event.key == pygame.K_l:
                    return ButtonPress(ButtonPress.ButtonType.CANCEL)

        return ButtonPress(ButtonPress.ButtonType.NONE)


class ButtonPress:
    class ButtonType(Enum):
        NONE = "NONE"
        UP = "UP"
        DOWN = "DOWN"
        SELECT = "SELECT"
        CANCEL = "CANCEL"

    def __init__(self, event_type):
        self.event_type = event_type

    def is_direction(self):
        return self.event_type == self.ButtonType.DOWN or \
               self.event_type == self.ButtonType.UP

    def is_action(self):
        return self.event_type == self.ButtonType.SELECT or \
               self.event_type == self.ButtonType.CANCEL
