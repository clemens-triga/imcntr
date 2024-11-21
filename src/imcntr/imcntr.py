from .imcntr_connection import SerialCommunication
from .imcntr_utils import Observer
import threading
import concurrent.futures

class CommandCommunication(SerialCommunication):
    """Expans :class:`SerialCommunication` with observers to be called when
    data is received or conncetion is lost.
    """
    def __init__(self, *args):
        super(CommandCommunication,self).__init__(*args)
        self.receive_observer = Observer()
        self.connection_lost_observer = Observer()

    def receive(self, data):
        """When called subsequently calls subscribed observers.

        ..:note: Method is called when new data is available at serial port
        """
        self.receive_observer.call(data)

    def connection_lost(self, e):
        """When connection is closed subsequently calls subscribed observers.
        """
        self.connection_lost_observer.call()
        super(CommandCommunication,self).connection_lost(e)


class Command():
    """Implements a watchdog for commands to take care of the expected answer to
    be sent back by the controller befor a timeout ouccres. Additionaly gives
    the possibility to wait for the answer by blocking the command sending thread.
    Also provides the possibility to be used in a context manger.

    :param protocol: Instance of :class:`CommandCommunication` with open conncetion
    :type protocol: instance
    :param command: Command to be sent to the controller
    :type command: str
    :param answer: Ansewer from controller corresponding to command
    :type answer: str
    :param watchdog:  Instance of :class:`ThreadPoolExecutor` with atleast one worker,
                      defaults to None.
    :type watchdog: instance
    :param timeout: timeout in seconds for watchdog
    :type timeout: float

    ..seealso:: <https://docs.python.org/dev/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor>
    """
    def __init__(self, protocol, command, answer, watchdog = None, timeout = None):
        self._protocol = protocol
        self._command = command
        self._answer = answer
        if not watchdog:
            self._watchdog = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        else:
            self._watchdog = watchdog
        self.timeout = timeout
        self.state = None
        self._receive_observer = self._protocol.receive_observer
        self._connection_lost_observer = self._protocol.connection_lost_observer
        self._connection_lost_observer.subscribe(self.shutdown)
        self._condition =  threading.Condition()
        self._future = concurrent.futures.Future()
        self._future.cancel() # future has to be cancelled so that done() returns True

    def __call__(self):
        """Transmit command to controller and start watchdog to check in answer is returnd before timeout."""
        if self._future.done():
            with self._condition:
                self._state = False
                self._receive_observer.subscribe(self._receive_task)
                self._protocol.send(self._command)
                self._future = self._watchdog.submit(self._watchdog_task, self.timeout)

    def wait(self, timeout = None):
        """Blocks until the answer was returned. If no timeout is passed the watchdog
        timeout is used

        :param timeout: time in seconds to be waited for answer, defaults to None
        :type timeout:
        :raise RuntimeError: If a timeout occures
        """
        timeout = timeout or self.timeout
        try:
            self._future.result(timeout = timeout)
        except Exception as e:
            raise RuntimeError(f"A timeout occured when waiting for  answer {self._answer} of command {self._command}!") from e

    def _watchdog_task(self, timeout):
        """ Task of watchdog therad.
        """
        with self._condition:
            if not self._condition.wait(timeout = self.timeout):
                raise RuntimeError(f"A timeout occured during command {self._command}!")
            self._receive_observer.unsubscribe(self._receive_task)

    def _receive_task(self, data):
        """Is called by receive observer when data was received
        """
        if data == self._answer:
            with self._condition :
                self._state = True
                self._condition.notify()

    def shutdown(self):
        """Stops watchdog when connection is closed.
        """
        with self._condition :
            self._condition.notify()
        self._connection_lost_observer.unsubscribe(self.shutdown)

    def __enter__(self):
        """ Enter context.
        """
        return self

    def __exit__(self, type, value, traceback):
        """Leave context, stop watchdog.
        """
        self.shutdown()


class _Advanced_Command(Command):
    """Prepare :class:`Command` to be used as parent class in specific command class.
    """
    _COMMAND = None
    _ANSWER = None
    _executor = None

    def __init__(self, *args, **kwargs ):
        super(_Advanced_Command,self).__init__(*args, command = self._COMMAND, answer = self._ANSWER, watchdog = self._executor, **kwargs)

class Out(_Advanced_Command):
    """Transmit command "move_out" and keepts track of answer "pos_out"
    """
    _COMMAND = "move_out"
    _ANSWER = "pos_out"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


class In(_Advanced_Command):
    """Transmit command "move_in" and keepts track of answer "pos_in"
    """
    _COMMAND = "move_in"
    _ANSWER = "pos_in"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


class Clockwise(_Advanced_Command):
    """Transmit command "rot_cw+STEPS" and keepts track of answer "rot_stopped"
    """
    _COMMAND = "rot_cw"
    _ANSWER = "rot_stopped"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def __call__(self, steps):
        """Befor transmitting command to controller adds :data:`steps`.

        :param steps: Number of steps to be rotated
        :type steps: int
        """
        self._COMMAND = self._COMMAND + '+' + steps
        super(Clockwise,self).__call__()


class CounterClockwise(_Advanced_Command):
    """Transmit command "rot_ccw+STEPS" and keepts track of answer "rot_stopped"
    """
    _COMMAND = "rot_ccw"
    _ANSWER = "rot_stopped"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def __call__(self, steps):
        """Befor transmitting command to controller adds :data:`steps`.

        :param steps: Number of steps to be rotated
        :type steps: int
        """
        self._COMMAND = self._COMMAND + '+' + steps
        super(CounterClockwise,self).__call__()


class Open(_Advanced_Command):
    """"Transmit command "open_shutter" and keepts track of answer "shutter_opened"
    """
    _COMMAND = "open_shutter"
    _ANSWER = "shutter_opened"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


class Close(_Advanced_Command):
    """"Transmit command "close_shutter" and keepts track of answer "shutter_closed"
    """
    _COMMAND = "close_shutter"
    _ANSWER = "shutter_closed"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


class StopMove(_Advanced_Command):
    """"Transmit command "stop_lin" and keepts track of answer "lin_stopped"
    """
    _COMMAND = "stop_lin"
    _ANSWER = "lin_stopped"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


class StopRotate(_Advanced_Command):
    """"Transmit command "stop_rot" and keepts track of answer "rot_stopped"
    """
    _COMMAND = "stop_rot"
    _ANSWER = "rot_stopped"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


class Stop(_Advanced_Command):
    """"Transmit command "stop_all" and keepts track of answer "all_stopped"
    """
    _COMMAND = "stop_all"
    _ANSWER = "all_stopped"
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


if __name__ == '__main__':
    exit(0)
