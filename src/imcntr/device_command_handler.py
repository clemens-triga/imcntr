from .device_connection import DeviceConnection
import threading

"""
Task and response helpers for a device connection.

This module provides utility classes for sending tasks to a device
and waiting for specific responses via given protocol using a threaded
observer pattern.
"""

class WaitForResponse:
    """
    Waits for a specific response from a connected device.

    An instance of this class subscribes to the protocol's receive observer and
    blocks until the expected response is received or a timeout occurs.

    The instance itself is callable and returns a boolean indicating whether the
    response was received within the timeout period.

    Note:
        Do not modify the `response` attribute while a wait is in progress. Doing
        so may result in missed signals or inconsistent behavior.

    :param protocol: Instance of SerialDeviceConnection` with an open connection.
    :type protocol: SerialDeviceConnection
    :param response: Expected response string to wait for.
    :type response: str
    :param timeout: Default timeout in seconds. If None, waits indefinitely.
    :type timeout: float | None
    """
    def __init__(self, protocol, response = None, timeout = None):
        self._protocol, self._receive_observer = self._validate_protocol(protocol)
        if response is not None:
            self._response = self._validate_signal(response)
        else:
            self._response = response
        if timeout is not None:
            self._timeout = self._validate_timeout(timeout)
        else:
            self._timeout = timeout
        self._event = threading.Event()

    @property
    def response(self):
        """Get the expected response string."""
        return self._response

    @response.setter
    def response(self, value):
        """
        Set a new expected response.

        :param value: New expected response string.
        :type value: str
        :raises TypeError: If the value is not a string.
        Note: Do not modify this while a wait is in progress.
        """
        self._response = self._validate_signal(value)

    @property
    def timeout(self):
        """Get the global timeout in seconds used when waiting for a response."""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Set the global timeout (must be positive number)."""
        self._timeout = self._validate_timeout(value)

    def _receive_message(self, data):
        """
        Callback invoked when data is received from the protocol.

        If the received data matches the expected response, the internal event
        is set, unblocking any thread that is currently waiting for this response.

        This is the core mechanism that allows WaitForResponse and SubmitTask
        to block until the expected response is received.

        :param data: Data received from the device.
        :type data: str
        """
        if data == self._response:
            self._event.set()

    def _validate_protocol(self, protocol):
        """
        Validate that the protocol exposes the required interface.

        The protocol must provide:
          - send(data: str)
          - receive_observer with subscribe(callback) and unsubscribe(callback)
        """
        if protocol is None:
            raise TypeError("Invalid protocol: must not be None")
        if not callable(getattr(protocol, "send", None)):
            raise TypeError(
                f"Invalid protocol: must implement send(), got '{type(protocol).__name__}'"
            )
        observer = getattr(protocol, "receive_observer", None)
        if observer is None:
            raise TypeError(
                f"Invalid protocol: must expose receive_observer, got '{type(protocol).__name__}'"
            )
        if not callable(getattr(observer, "subscribe", None)):
            raise TypeError(
                f"Invalid receive_observer: must implement subscribe(), got '{type(observer).__name__}'"
            )
        if not callable(getattr(observer, "unsubscribe", None)):
            raise TypeError(
                f"Invalid receive_observer: must implement unsubscribe(), got '{type(observer).__name__}'"
            )
        return protocol, observer

    def _validate_signal(self, value):
        """
        Validate a signal value. Signal is either a response or a task

        Ensures that the provided value is a string suitable for use as an
        expected response or as a task to be sent to the device.

        :param value: Signal or task value to validate.
        :type value: str
        :return: The validated signal or task value.
        :rtype: str
        :raises TypeError: If the value is not a string.
        """
        if not isinstance(value, str):
            raise TypeError(
                f"Invalid signal: must be of type str, got '{type(value).__name__}'"
            )
        return value

    def _validate_timeout(self, value):
        """
        Validate and normalize a timeout value.

        If `value` is None, the instance default timeout is used.
        Ensures that the timeout is a positive numeric value.

        :param value: Timeout value to validate.
        :type value: float | None
        :return: A validated timeout value.
        :rtype: float | None
        :raises TypeError: If the timeout is not a number.
        :raises ValueError: If the timeout is not a positive number.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Invalid timeout: must be of type int or float, got '{type(value).__name__}'"
            )
        if value <= 0:
            raise ValueError(f"Invalid timeout: must be non zero positive number, got '{value}'")
        return value

    def __call__(self, timeout = None):
        """
        Block until the expected response is received or a timeout occurs.

        If no timeout is provided, the instance default timeout is used.

        Note:
            This call is blocking and thread-safe.
            Do not change the `response` attribute during this call.

        :param timeout: Time in seconds to wait for the response.
                        If None, the instance timeout is used.
        :type timeout: float | None
        :return: True if the response was received before the timeout,
                 False if the timeout expired.
        :rtype: bool
        :raises ValueError: If the expected response is not set.
        """
        if timeout is not None:
            timeout = self._validate_timeout(timeout)
        else:
            timeout = self._timeout
        if self._response is None:
            raise ValueError(f"Response is not set yet, got '{self._response}'")
        self._event.clear()
        self._receive_observer.subscribe(self._receive_message)
        try:
            return self._event.wait(timeout)
        finally:
            self._receive_observer.unsubscribe(self._receive_message)
            self._event.clear()


class SubmitTask(WaitForResponse):
    """
    Sends a task to the device and optionally waits for a response.

    This class extends WaitForResponse by adding the ability to send a task
    via the protocol. The instance is callable and can either send the task
    without waiting or send the task and block until the expected response
    is received or a timeout occurs.

    Note:
        Do not modify the `response` attribute during the wait. Changing it
        while waiting may result in missed or incorrect signals.

    :param protocol: Instance of MessageExchange with an open connection.
    :type protocol: MessageExchange
    :param response: Expected response string to wait for.
    :type response: str
    :param task: Default task string to send to the device.
    :type task: str
    :param timeout: Default timeout in seconds. If None, waits indefinitely.
    :type timeout: float | None
    """
    def __init__(self, protocol, response, task=None, timeout=None):
        if task is not None:
            self._task = self._validate_signal(task)
        else:
            self._task = task
        super().__init__(protocol, response, timeout)

    @property
    def task(self):
        """Get the default task string to send to the device."""
        return self._task

    @task.setter
    def task(self, value):
        """
        Set a new default task string.

        :param value: Task string to set.
        :type value: str
        :raises TypeError: If the value is not a string.
        """
        self._task = self._validate_signal(value)

    def __call__(self, timeout=None, wait=False):
        """
        Send a task to the device and optionally wait for a response.

        If wait is False, the task is sent and the method returns immediately.
        If wait is True, the task is sent and the call blocks until the expected
        response is received or the timeout expires.

        Note:
            Uses the instance default task and expected response. Do not modify
            response during the call.


        :param timeout: Time in seconds to wait for the response.
                        If None, the instance timeout is used.
        :type timeout: float | None
        :param wait: Whether to wait for the response after sending the task.
        :type wait: bool
        :return: True if the response was received before the timeout when wait is True,
                 False if the timeout expired. Returns None when wait is False.
        :rtype: bool | None
        :raises ValueError: If the task is not set.
        Note: Do not change the `response` attribute during this call.
        """
        task = self._task
        if task is None:
            raise ValueError(f"Task is not set, got '{task}'")
        if not wait:
            self._protocol.send(task)
            return
        if timeout is not None:
            timeout = self._validate_timeout(timeout)
        else:
            timeout = self._timeout
        self._event.clear()
        self._receive_observer.subscribe(self._receive_message)
        try:
            self._protocol.send(task)
            return self._event.wait(timeout)
        finally:
            self._receive_observer.unsubscribe(self._receive_message)
            self._event.clear()
