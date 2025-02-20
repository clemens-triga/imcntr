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
        self.send_observer = Observer()
        self.receive_observer = Observer()
        self.connection_lost_observer = Observer()

    def send(self, data):
        """
        Called when to write data at serial port. It subsequently calls all the subscribed
        observers.

        :param e: Data to be written on serial port.
        :type e: Exception
        """
        self.send_observer.call(data)
        super(MessageExchange, self).send(data)

    def receive(self, data):
        """
        Called when new data is available at the serial port. It subsequently calls
        all the subscribed observers.

        :param data: Data received on serial port.
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

class WaitForResponse():
    """
    Provides the ability to wait for a given response from the connected controller until a timeout occurs. The desired response is defined by creating an instance.

    :param protocol: Instance of :class:`MessageExchange` with an open connection.
    :type protocol: :class:`MessageExchange`
    :param response: Response to be waited for.
    :type response: str
    :param timeout: Timeout in seconds to wait for response, defaults to None.
    :type timeout: float, optional
    """
    def __init__(self, protocol, response, timeout=None):
        self._protocol = protocol
        self.response = response
        self.timeout = timeout
        self._receive_observer = self._protocol.receive_observer
        self._condition = threading.Condition()

    def wait(self, timeout=None):
        """
        Blocks until the response is received. If no timeout is passed, the
        instance timeout is used.

        :param timeout: Time in seconds to wait for response. Defaults to None.
        :type timeout: float, optional
        :raise RuntimeError: If a timeout occurs before receiving the response.
        """
        timeout = timeout or self.timeout
        with self._condition:
            self._receive_observer.subscribe_first(self._receive_message)
            if not self._condition.wait(timeout=timeout):
                raise RuntimeError(f"A timeout occurred when waiting for controller response {self.response}!")
            self._receive_observer.unsubscribe(self._receive_message)

    def _receive_message(self, data):
        """
        Called by the receive observer when data is received.

        :param data: Data received from the controller.
        :type data: str
        """
        if data == self.response:
            with self._condition:
                self._state = True
                self._condition.notify()

class GiveOrder(WaitForResponse):
    """
    Expands :class:`WaitForResponse` with functionality for issue an order. The desired command is defined by creating an instance. Calling the instance sends it to the controller.

    :param protocol: Instance of :class:`MessageExchange` with an open connection.
    :type protocol: :class:`MessageExchange`
    :param response: Response to be waited for.
    :type response: str
    :param order: Order issued to controller.
    :type order: str
    """
    def __init__(self, *args, order = None, **kwargs):
        self.order = order
        super(GiveOrder, self).__init__(*args, **kwargs)

    def __call__(self, order = None):
        """
        Sends order to the controller via protocol. If no order is given instance order is passed.

        :param order: Order issued to controller.
        :type order: str
        """
        if order:
            self._protocol.send(order)
        else:
            self._protocol.send(self.order)

if __name__ == '__main__':
    exit(0)
