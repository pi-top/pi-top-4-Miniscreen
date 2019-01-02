import zmq
from ptcommon.ptdm_message import Message
from ptcommon.logger import PTLogger

zmq_socket = None


# Creates a server for sending messages to device manager
# Requests control of OLED
def _connect_to_socket():
    global zmq_socket

    zmq_context_send = zmq.Context()
    zmq_socket = zmq_context_send.socket(zmq.REQ)
    zmq_socket.sndtimeo = 1000
    zmq_socket.rcvtimeo = 1000
    zmq_socket.connect("tcp://127.0.0.1:3782")


def _send_request(message_request_id, parameters):
    message = Message.from_parts(message_request_id, parameters)
    zmq_socket.send_string(message.to_string())

    response_string = zmq_socket.recv_string()
    return Message.from_string(response_string)


def _cleanup():
    if zmq_socket is not None:
        zmq_socket.close(0)


def take_control_of_oled():
    message = None
    try:
        _connect_to_socket()
        message = _send_request(Message.REQ_SET_OLED_CONTROL, [str(1)])
    except Exception as e:
        PTLogger.warning("Error connecting to device manager: " + str(e))
    finally:
        _cleanup()
        return None if message is None else message.message_id() == Message.RSP_SET_OLED_CONTROL
