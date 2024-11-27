import serial
import serial.threaded

class SerialCommunication():
    """
    Provides tools for serial communication with the :mod:`serial.threaded` module to maintain a connection to an Arduino controller over the serial port.
    It also provides functionality to be used in a context manager.

    This class can be used to manage a serial connection and facilitate communication by sending and receiving data through the serial port.

    .. seealso:: <https://pyserial.readthedocs.io/en/latest/pyserial_api.html#module-serial.threaded>
    """
    def __init__(self, port=None):
        """
        Initializes the SerialCommunication instance with an optional serial port.

        :param port: The serial port to connect to (optional).
        :type port: str, optional
        """
        self._serial_connection = serial.Serial()
        self._thread = serial.threaded.ReaderThread(self._serial_connection, serial.threaded.LineReader)
        self.port = port

    @property
    def connection(self):
        """
        Returns the serial connection instance and the associated thread.

        By setting this property, the serial port for the connection is applied.

        :return: The serial connection and thread instance.
        :rtype: tuple
        """
        return self._serial_connection, self._thread

    @connection.setter
    def connection(self, port):
        """
        Sets the serial port for the connection.

        :param port: The port to use for the serial connection.
        :type port: str
        """
        self.port = port

    def connect(self):
        """
        Establishes the serial connection by opening the connection and starting the reader thread for reading and writing lines.
        Raises a :exc:`RuntimeError` if the connection fails.

        This method also prepares the connection for handling incoming data and managing the communication thread.
        """
        self._serial_connection.port = self.port
        self._connect_to_serial_port()
        self._start_serial_reader_thread()

    def _connect_to_serial_port(self):
        """
        Opens the serial connection and handles any exceptions that might occur during the process.

        :raises RuntimeError: If the connection cannot be established due to various exceptions (ValueError, SerialException, etc.)
        """
        try:
            self._serial_connection.open()
        except ValueError as e:
            raise RuntimeError("Parameter out of range when opening serial connection, connection failed!") from e
        except serial.SerialException as e:
            raise RuntimeError("Serial port not available, connection failed!") from e
        except Exception as e:
            raise RuntimeError("Unspecified error when opening serial connection!") from e

    def _start_serial_reader_thread(self):
        """
        Starts the serial read/write thread and waits for the connection to establish.
        It overrides the `handle_line` method from the :class:`LineReader` class with the :meth:`receive` method
        to provide the ability to modify behavior when a new line is received.

        :raises RuntimeError: If starting the thread fails.
        """
        try:
            self._thread.start()
            self.transport, self.protocol = self._thread.connect()
        except Exception as e:
            raise RuntimeError("Connecting communication thread failed!") from e
        # Assigning methods from pyserial LineReader class to own methods
        self.protocol.handle_line = self.receive
        self.protocol.connection_lost = self.connection_lost

    def disconnect(self):
        """
        Terminates the serial connection by stopping the reader thread and closing the connection.

        :raises RuntimeError: If the connection could not be closed properly.
        """
        try:
            self._thread.close()
        except Exception as e:
            raise RuntimeError("Connection not closed!") from e

    @property
    def connected(self):
        """
        Checks if the serial connection and the reader thread are both active.

        :return: True if the connection is open and the thread is alive, False otherwise.
        :rtype: bool
        """
        return self._serial_connection.is_open and self._thread.is_alive()

    def send(self, text):
        """
        Sends data to the serial port. If sending fails, raises a :exc:`RuntimeError`.

        :param text: The message to be written to the serial port.
        :type text: str
        :raises RuntimeError: If writing to the serial port fails.
        """
        try:
            self.protocol.write_line(text)
        except Exception as e:
            raise RuntimeError("Writing data to serial port failed!") from e

    def receive(self, data):
        """
        Called when data is received on the serial port. This method should be overridden by subclasses.

        :param data: The data received from the serial port.
        :type data: str
        :raises NotImplementedError: If the method is not overridden by a subclass.
        """
        raise NotImplementedError('Please implement functionality by overriding!')

    def connection_lost(self, e):
        """
        Called when the connection is closed. If the cause was an error, it is re-raised as :exc:`RuntimeError`.

        :param e: The exception that caused the connection loss.
        :type e: Exception
        :raises RuntimeError: If an exception caused the connection loss.
        """
        if isinstance(e, Exception):
            raise RuntimeError("Lost serial connection!") from e

    def __enter__(self):
        """
        Enter the context manager, establishes the serial connection, and raises :exc:`RuntimeError` if the connection fails.

        :raises RuntimeError: If the connection could not be opened.
        """
        self.connect()
        if not self.connected:
            raise RuntimeError("Connection not possible!")
        return self

    def __exit__(self, type, value, traceback):
        """
        Exit the context manager, disconnect from the serial port.

        This method ensures that the connection is closed when exiting the context.

        :param type: The exception type, if any.
        :param value: The exception value, if any.
        :param traceback: The traceback object, if any.
        """
        self.disconnect()


if __name__ == '__main__':
    exit(0)
