import serial
import serial.threaded
from .response_observer import Observer

"""
Serial communication utilities based on pySerial.

This module provides a high-level interface for line-based serial communication,
including threaded reading, observer-based receive handling, and extensible
callback hooks.
"""

class _SerialLineHandler(serial.threaded.LineReader):
    """
    A LineReader protocol for handling serial communication.

    Lines received from the serial port are forwarded to the assigned receiver via its
    `receive` method. Connection loss is reported to the receiver via `connection_lost`.
    """

    def __init__(self):
        """
        Initializes the _SerialLineHandler instance with no receiver.
        """
        super().__init__()
        self._receiver = None

    @property
    def receiver(self):
        """
        Gets the current receiver of the protocol.

        :return: The receiver instance that handles incoming data.
        """
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        """
        Sets the receiver instance for handling incoming data.

        :param value: An object with `receive(data)` and `connection_lost(exception)` methods.
        """
        self._receiver = value

    def connection_lost(self, exc):
        """
        Called automatically when the serial connection is lost.

        Forwards the exception to the receiver's `connection_lost` method.

        :param exc: The exception that caused the connection loss.
        :type exc: Exception
        """
        if self._receiver is not None:
            self._receiver.connection_lost(exc)

    def handle_line(self, line):
        """
        Called automatically when a new line is received from the serial port.

        Forwards the received line to the receiver's `receive` method.

        :param line: A line of data received from the serial port.
        :type line: str
        """
        if self._receiver is not None:
            self._receiver.receive(line)



class DeviceConnection:
    """
    Manages serial connection with a device over a serial port using thread.

    Provides methods to connect, disconnect, send, and receive data.
    Supports context manager usage to automatically handle connections.
    """

    def __init__(self, port=None):
        """
        Initializes the SerialCommunication instance with an optional serial port.

        :param port: The serial port to connect to (optional).
        :type port: str, optional
        """
        self._port = None
        if port is not None:
            self.port = port
        self._serial_connection = None
        self._thread = None
        self._transport = None
        self._protocol = None
        self._receive_observer = Observer()

    @property
    def connected(self):
        """
        Checks if the serial connection and reader thread are active.

        :return: True if connected and reader thread is alive, False otherwise.
        :rtype: bool
        """
        return bool(
            self._serial_connection
            and self._serial_connection.is_open
            and self._thread
            and self._thread.is_alive()
        )

    @property
    def connection(self):
        """
        Returns the current serial connection object.

        :return: The serial connection instance or None if not connected.
        :rtype: serial.Serial or None
        """
        return self._serial_connection

    @property
    def port(self):
        """
        Returns the currently configured serial port.

        :return: The serial port as a string.
        :rtype: str or None
        """
        return self._port

    @port.setter
    def port(self, value):
        """
        Sets the serial port for the connection.

        :param value: The serial port to use (e.g., 'COM3' or '/dev/ttyUSB0').
        :type value: str
        :raises TypeError: If the value is not a string.
        """
        if not isinstance(value, str):
            raise TypeError("port must be a string")
        self._port = value

    @property
    def receive_observer(self):
        """
        Returns the Observer used to notify subscribers when data is received.

        Subscribers will be called with the received data string.

        :return: Observer instance for received data.
        :rtype: Observer
        """
        return self._receive_observer

    @property
    def thread(self):
        """
        Returns the ReaderThread instance managing the serial connection.

        :return: The ReaderThread instance or None if not started.
        :rtype: serial.threaded.ReaderThread or None
        """
        return self._thread

    def connect(self):
        """
        Establishes the serial connection and starts the read/write thread.

        :raises ValueError: If the serial port is not specified.
        :raises RuntimeError: If the connection is already established or fails.
        """
        if not self._port:
            raise ValueError("Serial port must be specified before connecting")
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Connection already established")
        self._connect_to_serial_port()
        self._start_serial_reader_thread()

    def connection_lost(self, exception):
        """
        Called when the connection is closed or lost.

        This method resets the internal connection state and then invokes
        `connection_lost_callback`.

        :param exception: The exception that caused the connection loss.
        :type exception: Exception
        """
        self._reset_connection()
        self.connection_lost_callback(exception)

    def connection_lost_callback(self, exception):
        """
        Optional hook called when the connection is closed or lost.

        Override in a subclass to handle connection loss.

        :param exception: The exception that caused the connection loss.
        :type exception: Exception
        """
        pass

    def disconnect(self):
        """
        Stops the reader thread and closes the serial connection.

        :raises RuntimeError: If the connection cannot be closed properly.
        """
        try:
            if self._thread and self._thread.is_alive():
                self._thread.close()
            if self._serial_connection and self._serial_connection.is_open:
                self._serial_connection.close()
        except Exception as e:
            raise RuntimeError("Connection not closed!") from e
        else:
            self._reset_connection()

    def receive(self, data):
        """
        Called when data is received from the serial port.

        Calls all subscribed observers and triggers `receive_callback`.

        :param data: Data received from the serial port.
        :type data: str
        """
        self._receive_observer.call(data)
        self.receive_callback(data)

    def receive_callback(self, data):
        """
        Optional hook called when new data is received.

        Override in a subclass to handle incoming data.

        Note:
            Callbacks and observers are executed in the serial reader thread,
            not in the main thread.


        :param data: The received data.
        :type data: str
        """
        pass

    def send(self, data):
        """
        Sends a string message over the serial connection.

        :param data: The message to send.
        :type data: str
        :raises RuntimeError: If the connection is not active or sending fails.
        """
        if not self.connected:
            raise RuntimeError("Not connected to serial port")
        try:
            self._protocol.write_line(data)
        except Exception as e:
            raise RuntimeError("Writing data to serial port failed!") from e
        self.send_callback(data)

    def send_callback(self, data):
        """
        Optional hook called after data has been successfully sent.

        Override in a subclass to perform actions after sending data.

        :param data: The sent data.
        :type data: str
        """
        pass

    def _connect_to_serial_port(self):
        """
        Opens the serial connection using the configured port.

        :raises RuntimeError: If the connection fails due to invalid parameters,
                              unavailable port, or other exceptions.
        """
        try:
            self._serial_connection = serial.Serial(self._port)
        except ValueError as e:
            raise RuntimeError("Parameter out of range when opening serial connection") from e
        except serial.SerialException as e:
            raise RuntimeError("Serial port not available") from e
        except Exception as e:
            raise RuntimeError("Unspecified error when opening serial connection") from e

    def _reset_connection(self):
        """
        Resets all internal connection-related state.

        This method clears the serial connection, reader thread, transport,
        and protocol references. It is called after a clean disconnect or
        when the connection is lost.

        This is an internal method and should not be called directly.
        """
        self._serial_connection = None
        self._thread = None
        self._transport = None
        self._protocol = None

    def _start_serial_reader_thread(self):
        """
        Starts a threaded reader/writer for the serial connection.

        Initializes the protocol, sets the receiver, and starts the ReaderThread.

        :raises RuntimeError: If the thread fails to start.
        """
        self._thread = serial.threaded.ReaderThread(self._serial_connection, _SerialLineHandler)
        self._transport, self._protocol = self._thread.connect()
        self._protocol.receiver = self
        try:
            self._thread.start()
        except Exception as e:
            raise RuntimeError("Connecting communication thread failed!") from e

    def __enter__(self):
        """
        Enter a context manager, establishing the serial connection.

        :raises RuntimeError: If the connection cannot be opened.
        :return: The SerialCommunication instance.
        """
        self.connect()
        if not self.connected:
            raise RuntimeError("Connection not possible!")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit a context manager and disconnect the serial connection.

        Exceptions during disconnection are suppressed. Exceptions in the `with` block
        are propagated.

        :param exc_type: Exception type if raised, else None.
        :param exc_value: Exception value if raised, else None.
        :param traceback: Traceback object if an exception occurred, else None.
        :return: False to propagate exceptions from the `with` block.
        """
        try:
            self.disconnect()
        except Exception:
            pass
        return False
