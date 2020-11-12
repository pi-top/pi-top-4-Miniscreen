from components.ButtonPress import ButtonPress
from pitop.utils.logger import PTLogger
from pitop.utils.ptdm_message import Message
from threading import Thread
from time import sleep
import traceback
import zmq


# Creates a client for publish messages from device manager
# Listens for button presses
class SubscriberClient:
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
        PTLogger.debug("Opening subscriber socket...")

        try:
            self._zmq_socket.connect("tcp://127.0.0.1:3781")
            PTLogger.info("Subscriber client ready.")

        except zmq.error.ZMQError as e:
            PTLogger.error("Error starting the subscriber client: " + str(e))
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
        PTLogger.info("Listening for events...")

        while self._continue:
            poller = zmq.Poller()
            poller.register(self._zmq_socket, zmq.POLLIN)

            events = poller.poll(500)
            for i in range(len(events)):
                message_string = self._zmq_socket.recv_string()
                message = Message.from_string(message_string)

                if message.message_id() == Message.PUB_BATTERY_STATE_CHANGED:
                    message.validate_parameters([int, int, int, int])
                    charging_state, capacity, time_remaining, wattage = (
                        message.parameters()
                    )
                    self._callback_client.update_battery_state(
                        charging_state, capacity)

                elif message.message_id() == Message.PUB_V3_BUTTON_UP_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(
                        ButtonPress(ButtonPress.ButtonType.UP)
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_DOWN_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(
                        ButtonPress(ButtonPress.ButtonType.DOWN)
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_SELECT_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(
                        ButtonPress(ButtonPress.ButtonType.SELECT)
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_CANCEL_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.add_button_press_to_stack(
                        ButtonPress(ButtonPress.ButtonType.CANCEL)
                    )
