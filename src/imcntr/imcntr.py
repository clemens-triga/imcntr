from .imcntr_connection import SerialCommunication
from .imcntr_communication import MessageExchange, WaitForMessage, SendMessage
from .imcntr_utils import Observer
import threading
import concurrent.futures


class _Advanced_Wait(WaitForMessage):
    """Prepare :class:`WaitForMessage` to be used as a parent class by only giving the expected message as a class constant.
    """
    _EXPECTED_MESSAGE = None

    def __init__(self, *args, **kwargs ):
        super(_Advanced_Wait, self).__init__(*args, message=self._EXPECTED_MESSAGE, **kwargs)

class _Advanced_Command(SendMessage):
    """Prepare :class:`SendMessage` to be used as a parent class by only giving the outgoing command and expected message as class constants.
    """
    _OUTGOING_MESSAGE = None
    _EXPECTED_MESSAGE = None

    def __init__(self, *args, **kwargs ):
        super(_Advanced_Command, self).__init__(*args, command=self._OUTGOING_MESSAGE, message=self._EXPECTED_MESSAGE, **kwargs)

class Ready(_Advanced_Wait):
    """Offers a method to wait for the message "controller_ready". The controller sends this message after successful startup.
    """
    _EXPECTED_MESSAGE = "controller_ready"


class Connected(_Advanced_Command):
    """Check if the controller is connected by transmitting the command "connect" when called. Also offers to wait for the message "connected".
    """
    _OUTGOING_MESSAGE = "connect"
    _EXPECTED_MESSAGE = "connected"


class Out(_Advanced_Command):
    """Moves the sample out by transmitting the command "move_out" when called. Also offers to wait for the message "pos_out" after the movement is finished.
    """
    _OUTGOING_MESSAGE = "move_out"
    _EXPECTED_MESSAGE = "pos_out"

class In(_Advanced_Command):
    """Moves the sample in by transmitting the command "move_in" when called. Also offers to wait for the message "pos_in" after the movement is finished.
    """
    _OUTGOING_MESSAGE = "move_in"
    _EXPECTED_MESSAGE = "pos_in"

class Clockwise(_Advanced_Command):
    """Rotates the sample clockwise by the given steps by sending the "rot_cw+STEPS" command when called. Also offers to wait for the message "rot_stopped" after the movement is finished.
    """
    _OUTGOING_MESSAGE = "rot_cw"
    _EXPECTED_MESSAGE = "rot_stopped"

    def __call__(self, steps):
        """Before transmitting the command to the controller, adds :data:`steps`.

        :param steps: Number of steps to be rotated
        :type steps: int
        """
        self._OUTGOING_MESSAGE = self._OUTGOING_MESSAGE + '+' + str(steps)
        super(Clockwise, self).__call__()

class CounterClockwise(_Advanced_Command):
    """Rotates the sample counterclockwise by the given steps by sending the "rot_ccw+STEPS" command when called. Also offers to wait for the message "rot_stopped" after the movement is finished.
    """
    _OUTGOING_MESSAGE = "rot_ccw"
    _EXPECTED_MESSAGE = "rot_stopped"

    def __call__(self, steps):
        """Before transmitting the command to the controller, adds :data:`steps`.

        :param steps: Number of steps to be rotated
        :type steps: int
        """
        self._OUTGOING_MESSAGE = self._OUTGOING_MESSAGE + '+' + str(steps)
        super(CounterClockwise, self).__call__()

class Open(_Advanced_Command):
    """Opens the shutter by transmitting the command "open_shutter" when called. Also offers to wait for the message "shutter_opened" after the shutter is opened.
    """
    _OUTGOING_MESSAGE = "open_shutter"
    _EXPECTED_MESSAGE = "shutter_opened"


class Close(_Advanced_Command):
    """Closes the shutter by transmitting the command "close_shutter" when called. Also offers to wait for the message "shutter_closed" after the shutter is closed.
    """
    _OUTGOING_MESSAGE = "close_shutter"
    _EXPECTED_MESSAGE = "shutter_closed"


class StopMove(_Advanced_Command):
    """Stops linear movement by transmitting the command "stop_lin" when called. Also offers to wait for the message "lin_stopped" after the stop has taken place.
    """
    _OUTGOING_MESSAGE = "stop_lin"
    _EXPECTED_MESSAGE = "lin_stopped"

class StopRotate(_Advanced_Command):
    """Stops rotational movement by transmitting the command "stop_rot" when called. Also offers to wait for the message "rot_stopped" after the stop has taken place.
    """
    _OUTGOING_MESSAGE = "stop_rot"
    _EXPECTED_MESSAGE = "rot_stopped"

class Stop(_Advanced_Command):
    """Stops all movement by transmitting the command "stop_all" when called. Also offers to wait for the message "all_stopped" after the stop has taken place.
    """
    _OUTGOING_MESSAGE = "stop_all"
    _EXPECTED_MESSAGE = "all_stopped"


class Controller():
    """Prvides a set of functionality
    """
    def __init__(self, *args, **kwargs):
        self.ready = Ready(*args, **kwargs)
        self.connected = Connected(*args, **kwargs)

class Sample():
    def __init__(self, *args, **kwargs):
        self.move_out = Out(*args, **kwargs)
        self.move_in = In(*args, **kwargs)
        self.move_stop = StopMove(*args, **kwargs)
        self.rotate_cw = Clockwise(*args, **kwargs)
        self.rotate_ccw = CounterClockwise(*args, **kwargs)
        self.rotate_stop = StopRotate(*args, **kwargs)
        self.stop = Stop(*args, **kwargs)


class Shutter():

    def __init__(self, *args, **kwargs):
        self.open = Open(*args, **kwargs)
        self.close = Close(*args, **kwargs)


if __name__ == '__main__':
    exit(0)
