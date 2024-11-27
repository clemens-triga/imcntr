from .imcntr_connection import SerialCommunication
from .imcntr_utils import Observer
import threading

class MessageExchange(SerialCommunication):
    """
    Expands :class:`SerialCommunication` with observers to be called when data is received
    or connection is lost.

    :param args: Arguments passed to the parent :class:`SerialCommunication` class.
    :param kwargs: Keyword arguments passed to the parent :class:`SerialCommunication` class.
    """
    def __init__(self, *args, **kwargs):
        super(MessageExchange, self).__init__(*args)
        self.receive_observer = Observer()
        self.connection_lost_observer = Observer()

    def receive(self, data):
        """
        Called when new data is available at the serial port. It subsequently calls
        all the subscribed observers.

        :param data: Data received on the serial port.
        :type data: str
        """
        self.receive_observer.call(data)

    def connection_lost(self, e):
        """
        Called when the connection is closed. It subsequently calls all the subscribed
        observers for connection loss.

        :param e: The exception that caused the connection to be lost.
        :type e: Exception
        """
        self.connection_lost_observer.call()
        super(MessageExchange, self).connection_lost(e)

class WaitForMessage():
    """
    Provides the ability to wait for an incoming message from the connected controller
    until a timeout occurs.

    :param protocol: Instance of :class:`MessageExchange` with an open connection.
    :type protocol: :class:`MessageExchange`
    :param message: Incoming message to be waited for.
    :type message: str
    :param timeout: Timeout in seconds to wait, defaults to None.
    :type timeout: float, optional
    """
    def __init__(self, protocol, message, timeout=None):
        self._protocol = protocol
        self.expect_message = message
        self.timeout = timeout
        self._receive_observer = self._protocol.receive_observer
        self._condition = threading.Condition()

    def wait(self, timeout=None):
        """
        Blocks until the expected message is received. If no timeout is passed, the
        instance timeout is used.

        :param timeout: Time in seconds to wait for the message. Defaults to None.
        :type timeout: float, optional
        :raise RuntimeError: If a timeout occurs before receiving the expected message.
        """
        timeout = timeout or self.timeout
        with self._condition:
            self._receive_observer.subscribe(self._receive_message)
            if not self._condition.wait(timeout=timeout):
                raise RuntimeError(f"A timeout occurred when waiting for incoming message {self.expect_message}!")
            self._receive_observer.unsubscribe(self._receive_message)

    def _receive_message(self, data):
        """
        Called by the receive observer when data is received.

        :param data: Data received from the controller.
        :type data: str
        """
        if data == self.expect_message:
            with self._condition:
                self._state = True
                self._condition.notify()

class SendMessage(WaitForMessage):
    """
    Expands :class:`WaitForMessage` with functionality for sending a defined command by
    calling the instance.

    :param protocol: Instance of :class:`MessageExchange` with an open connection.
    :type protocol: :class:`MessageExchange`
    :param message: Incoming message to be waited for.
    :type message: str
    :param command: Command to be sent to the controller.
    :type command: str
    """
    def __init__(self, *args, command, **kwargs):
        self.outgoing_command = command
        super(SendMessage, self).__init__(*args, **kwargs)

    def __call__(self):
        """
        Sends the command to the controller via the protocol.

        :raises RuntimeError: If sending the message fails.
        """
        self._protocol.send(self.outgoing_command)

if __name__ == '__main__':
    exit(0)
