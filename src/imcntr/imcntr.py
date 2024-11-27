from .imcntr_connection import SerialCommunication
from .imcntr_communication import MessageExchange, WaitForMessage, SendMessage
from .imcntr_utils import Observer
import threading
import concurrent.futures


class _Advanced_Wait(WaitForMessage):
    """
    A base class for waiting for a specific message from the controller. This class
    extends :class:`WaitForMessage` and simplifies the usage by setting the expected
    message as a class constant.

    :param args: Arguments passed to the parent :class:`WaitForMessage` class.
    :param kwargs: Keyword arguments passed to the parent :class:`WaitForMessage` class.

    :ivar _EXPECTED_MESSAGE: The message to wait for.
    :type _EXPECTED_MESSAGE: str or None
    """

    _EXPECTED_MESSAGE = None

    def __init__(self, *args, **kwargs):
        """
        Initializes the wait instance, setting the expected message.

        :param args: Arguments passed to the parent :class:`WaitForMessage`.
        :param kwargs: Keyword arguments passed to the parent :class:`WaitForMessage`.
        """
        super(_Advanced_Wait, self).__init__(*args, message=self._EXPECTED_MESSAGE, **kwargs)


class _Advanced_Command(SendMessage):
    """
    A base class for sending commands to the controller and waiting for a response.
    This class extends :class:`SendMessage` and simplifies usage by setting the outgoing
    command and expected response message as class constants.

    :param args: Arguments passed to the parent :class:`SendMessage` class.
    :param kwargs: Keyword arguments passed to the parent :class:`SendMessage` class.

    :ivar _OUTGOING_MESSAGE: The outgoing message to send to the controller.
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response from the controller after sending the command.
    :type _EXPECTED_MESSAGE: str
    """

    _OUTGOING_MESSAGE = None
    _EXPECTED_MESSAGE = None

    def __init__(self, *args, **kwargs):
        """
        Initializes the command instance, setting the outgoing message and expected response.

        :param args: Arguments passed to the parent :class:`SendMessage`.
        :param kwargs: Keyword arguments passed to the parent :class:`SendMessage`.
        """
        super(_Advanced_Command, self).__init__(*args, command=self._OUTGOING_MESSAGE, message=self._EXPECTED_MESSAGE, **kwargs)


class Ready(_Advanced_Wait):
    """
    Waits for the message `"controller_ready"`. The controller sends this message
    after a successful startup.

    :param args: Arguments passed to the parent :class:`_Advanced_Wait` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Wait` class.
    """
    _EXPECTED_MESSAGE = "controller_ready"


class Connected(_Advanced_Command):
    """
    Sends the `"connect"` command to the controller and waits for the response `"connected"`.
    This checks if the controller is successfully connected.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"connect"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"connected"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "connect"
    _EXPECTED_MESSAGE = "connected"


class Out(_Advanced_Command):
    """
    Sends the `"move_out"` command to move the sample out and waits for the response `"pos_out"`
    after the movement is finished.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"move_out"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"pos_out"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "move_out"
    _EXPECTED_MESSAGE = "pos_out"


class In(_Advanced_Command):
    """
    Sends the `"move_in"` command to move the sample in and waits for the response `"pos_in"`
    after the movement is finished.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"move_in"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"pos_in"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "move_in"
    _EXPECTED_MESSAGE = "pos_in"


class Clockwise(_Advanced_Command):
    """
    Sends the `"rot_cw+STEPS"` command to rotate the sample clockwise by the given number
    of steps. Waits for the response `"rot_stopped"` after the rotation is finished.

    :param steps: The number of steps to rotate the sample.
    :type steps: int

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"rot_cw"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"rot_stopped"`).
    :type _EXPECTED_MESSAGE: str
    """

    _OUTGOING_MESSAGE = "rot_cw"
    _EXPECTED_MESSAGE = "rot_stopped"

    def __call__(self, steps):
        """
        Adds the number of steps to the rotation command and sends it to the controller.

        :param steps: The number of steps to rotate the sample clockwise.
        :type steps: int
        """
        self._OUTGOING_MESSAGE = self._OUTGOING_MESSAGE + '+' + str(steps)
        super(Clockwise, self).__call__()


class CounterClockwise(_Advanced_Command):
    """
    Sends the `"rot_ccw+STEPS"` command to rotate the sample counterclockwise by the given
    number of steps. Waits for the response `"rot_stopped"` after the rotation is finished.

    :param steps: The number of steps to rotate the sample.
    :type steps: int

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"rot_ccw"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"rot_stopped"`).
    :type _EXPECTED_MESSAGE: str
    """

    _OUTGOING_MESSAGE = "rot_ccw"
    _EXPECTED_MESSAGE = "rot_stopped"

    def __call__(self, steps):
        """
        Adds the number of steps to the rotation command and sends it to the controller.

        :param steps: The number of steps to rotate the sample counterclockwise.
        :type steps: int
        """
        self._OUTGOING_MESSAGE = self._OUTGOING_MESSAGE + '+' + str(steps)
        super(CounterClockwise, self).__call__()


class Open(_Advanced_Command):
    """
    Sends the `"open_shutter"` command to open the shutter and waits for the response
    `"shutter_opened"` after the shutter is opened.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"open_shutter"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"shutter_opened"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "open_shutter"
    _EXPECTED_MESSAGE = "shutter_opened"


class Close(_Advanced_Command):
    """
    Sends the `"close_shutter"` command to close the shutter and waits for the response
    `"shutter_closed"` after the shutter is closed.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"close_shutter"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"shutter_closed"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "close_shutter"
    _EXPECTED_MESSAGE = "shutter_closed"


class StopMove(_Advanced_Command):
    """
    Sends the `"stop_lin"` command to stop linear movement and waits for the response `"lin_stopped"`
    after the stop.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"stop_lin"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"lin_stopped"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "stop_lin"
    _EXPECTED_MESSAGE = "lin_stopped"


class StopRotate(_Advanced_Command):
    """
    Sends the `"stop_rot"` command to stop rotational movement and waits for the response `"rot_stopped"`
    after the stop.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"stop_rot"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"rot_stopped"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "stop_rot"
    _EXPECTED_MESSAGE = "rot_stopped"


class Stop(_Advanced_Command):
    """
    Sends the `"stop_all"` command to stop all movement and waits for the response `"all_stopped"`
    after the stop.

    :param args: Arguments passed to the parent :class:`_Advanced_Command` class.
    :param kwargs: Keyword arguments passed to the parent :class:`_Advanced_Command` class.

    :ivar _OUTGOING_MESSAGE: The outgoing command (`"stop_all"`).
    :type _OUTGOING_MESSAGE: str
    :ivar _EXPECTED_MESSAGE: The expected response (`"all_stopped"`).
    :type _EXPECTED_MESSAGE: str
    """
    _OUTGOING_MESSAGE = "stop_all"
    _EXPECTED_MESSAGE = "all_stopped"


class Controller():
    """
    Provides methods to interact with the controller, such as checking if it's ready and connected.

    :ivar ready: The instance for checking if the controller is ready.
    :type ready: :class:`Ready`
    :ivar connected: The instance for checking if the controller is connected.
    :type connected: :class:`Connected`
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the controller and checks readiness and connection.

        :param args: Arguments passed to the :class:`Ready` and :class:`Connected` classes.
        :param kwargs: Keyword arguments passed to the :class:`Ready` and :class:`Connected` classes.
        """
        self.ready = Ready(*args, **kwargs)
        self.connected = Connected(*args, **kwargs)


class Sample():
    """
    Provides methods to move the sample in or out, rotate, and stop movements.

    :ivar move_out: The instance for moving the sample out.
    :type move_out: :class:`Out`
    :ivar move_in: The instance for moving the sample in.
    :type move_in: :class:`In`
    :ivar move_stop: The instance for stopping linear movement.
    :type move_stop: :class:`StopMove`
    :ivar rotate_cw: The instance for rotating the sample clockwise.
    :type rotate_cw: :class:`Clockwise`
    :ivar rotate_ccw: The instance for rotating the sample counterclockwise.
    :type rotate_ccw: :class:`CounterClockwise`
    :ivar rotate_stop: The instance for stopping rotational movement.
    :type rotate_stop: :class:`StopRotate`
    :ivar stop: The instance for stopping all movements.
    :type stop: :class:`Stop`
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the sample and provides movement and rotation functionality.

        :param args: Arguments passed to the respective command classes.
        :param kwargs: Keyword arguments passed to the respective command classes.
        """
        self.move_out = Out(*args, **kwargs)
        self.move_in = In(*args, **kwargs)
        self.move_stop = StopMove(*args, **kwargs)
        self.rotate_cw = Clockwise(*args, **kwargs)
        self.rotate_ccw = CounterClockwise(*args, **kwargs)
        self.rotate_stop = StopRotate(*args, **kwargs)
        self.stop = Stop(*args, **kwargs)


class Shutter():
    """
    Provides methods to open or close the shutter.

    :ivar open: The instance for opening the shutter.
    :type open: :class:`Open`
    :ivar close: The instance for closing the shutter.
    :type close: :class:`Close`
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the shutter control functionality.

        :param args: Arguments passed to the respective command classes.
        :param kwargs: Keyword arguments passed to the respective command classes.
        """
        self.open = Open(*args, **kwargs)
        self.close = Close(*args, **kwargs)


if __name__ == '__main__':
    exit(0)
