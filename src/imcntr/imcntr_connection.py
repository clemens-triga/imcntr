from .imcntr_connection import SerialCommunication
from .imcntr_utils import Observer
import threading
import concurrent.futures

class MessageExchange(SerialCommunication):
    """
    Extends the :class:`SerialCommunication` class by adding observer functionality.
    This allows observers to be notified when new data is received or when the connection is lost.

    Observers can be subscribed to handle specific events like data reception or connection loss.

    :param args: Arguments passed to the parent :class:`SerialCommunication` class.
    :param kwargs: Keyword arguments passed to the parent :class:`SerialCommunication` class.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the MessageExchange instance, setting up observers for data reception
        and connection loss events.

        :param args: Arguments passed to the parent :class:`SerialCommunication` class.
        :param kwargs: Keyword arguments passed to the parent :class:`SerialCommunication` class.
        """
        super(MessageExchange, self).__init__(*args, **kwargs)
        self.receive_observer = Observer()  # Observer for data reception
        self.connection_lost_observer = Observer()  # Observer for connection loss

    def receive(self, data):
        """
        Called when new data is received at the serial port.
        This method triggers the `receive_observer` to notify all subscribed observers.

        :param data: The data received from the serial port.
        :type data: str
        """
        self.receive_observer.call(data)  # Notify all subscribed observers with the received data

    def connection_lost(self, e):
        """
        Called when the connection is lost.
        This method triggers the `connection_lost_observer` to notify all subscribed observers.

        :param e: The exception or error that caused the connection loss.
        :type e: Exception
        """
        self.connection_lost_observer.call()  # Notify all subscribed observers about the connection loss
        super(MessageExchange, self).connection_lost(e)  # Call the parent class method to handle connection loss

class WaitForMessage():
    """
    Provides functionality to wait for a specific incoming message from the connected controller.
    The class will block until the expected message is received or a timeout occurs.

    :param protocol: Instance of :class:`MessageExchange` with an open connection.
    :type protocol: :class:`MessageExchange`
    :param message: The message that is expected from the controller.
    :type message: str
    :param timeout: Timeout duration in seconds, defaults to None (waits indefinitely).
    :type timeout: float, optional
    """

    def __init__(self, protocol, message, timeout=None):
        """
        Initializes the WaitForMessage instance.

        :param protocol: The instance of :class:`MessageExchange` that has an open serial connection.
        :param message: The specific message to wait for from the controller.
        :param timeout: Timeout value in seconds (defaults to None).
        """
        self._protocol = protocol  # The protocol instance used to send/receive messages
        self.expect_message = message  # The message to wait for
        self.timeout = timeout  # The timeout duration for waiting
        self._receive_observer = self._protocol.receive_observer  # Observer for receiving messages
        self._condition = threading.Condition()  # Condition variable for synchronizing the wait

    def wait(self, timeout=None):
        """
        Blocks the current thread until the expected message is received or a timeout occurs.

        :param timeout: Timeout value in seconds, overrides instance timeout if provided.
        :type timeout: float, optional
        :raise RuntimeError: If a timeout occurs before receiving the expected message.
        """
        timeout = timeout or self.timeout  # Use instance timeout if no timeout is provided
        with self._condition:
            # Subscribe to the receive observer to be notified when data is received
            self._receive_observer.subscribe(self._receive_message)
            # Wait until the expected message is received or timeout occurs
            if not self._condition.wait(timeout=timeout):
                raise RuntimeError(f"A timeout occurred when waiting for incoming message {self.expect_message}!")
            # Unsubscribe after the message has been received
            self._receive_observer.unsubscribe(self._receive_message)

    def _receive_message(self, data):
        """
        Called by the receive observer when data is received. This method checks if the received
        message matches the expected message and notifies the waiting thread if it does.

        :param data: The data received from the serial port.
        :type data: str
        """
        if data == self.expect_message:
            with self._condition:
                self._state = True  # Set the state to True, indicating the message was received
                self._condition.notify()  # Notify the waiting thread

class SendMessage(WaitForMessage):
    """
    Extends :class:`WaitForMessage` by adding the functionality to send a command to the controller.
    This allows sending a defined message and waiting for a response in a single operation.

    :param command: Command to be sent to the controller.
    :type command: str
    """

    def __init__(self, *args, command, **kwargs):
        """
        Initializes the SendMessage instance with the outgoing command and protocol.

        :param command: The command to send to the controller.
        :param args: Arguments passed to the parent :class:`WaitForMessage` class.
        :param kwargs: Keyword arguments passed to the parent :class:`WaitForMessage` class.
        """
        self.outgoing_command = command  # The command that will be sent to the controller
        super(SendMessage, self).__init__(*args, **kwargs)  # Initialize the parent class

    def __call__(self):
        """
        Sends the outgoing command to the controller via the protocol's send method.
        """
        self._protocol.send(self.outgoing_command)  # Send the command to the controller

if __name__ == '__main__':
    exit(0)
