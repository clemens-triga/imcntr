import serial
import serial.threaded

class SerialCommunication():
    """Provides tools for serial connection with :mod:`serial.threaded` module to maintain a connection to an Arduino controller over the serial port. Also provides the possibility to be used in a context manager.

    .. seealso:: <https://pyserial.readthedocs.io/en/latest/pyserial_api.html#module-serial.threaded>
    """
    def __init__(self, port=None):
        """Constructor method"""
        self._serial_connection = serial.Serial()
        self._thread = serial.threaded.ReaderThread(self._serial_connection, serial.threaded.LineReader)
        self.port = port
        #self.ports = []
        #for port in serial.tools.list_ports.comports():
        #    if ('ACM' or 'USB') in port.device:
        #        self.ports.append(port.device)

    @property
    def connection(self):
        """Get serial instance to run the serial connection. By setting :meth:`connection`, the port for the serial connection is applied.

        :param port: Port for serial connection
        :type port: str
        :return: serial and thread instance
        :rtype: object
        """
        return self._serial_connection, self._thread

    @connection.setter
    def connection(self, port):
        self.port = port

    def connect(self):
        """Connects to serial port by opening :obj:`connection` and starts :obj:`thread`
        for reading and writing lines at the port. If there are exceptions during
        establishing the connection, they are re-raised as :exc:`RuntimeError`.
        """
        self._serial_connection.port = self.port
        self._connect_to_serial_port()
        self._start_serial_reader_thread()

    def _connect_to_serial_port(self):
        """Opens :obj:`connection` and catches potential exceptions."""
        try:
            self._serial_connection.open()
        except ValueError as e:
            raise RuntimeError("Parameter out of range when opening serial connection, connection failed!") from e
        except serial.SerialException as e:
            raise RuntimeError(
                  "Serial port not available, connection failed!") from e
        except Exception as e:
            raise RuntimeError("Unspecified error when opening serial connection!") from e

    def _start_serial_reader_thread(self):
        """Starts serial read/write :obj:`thread` and waits for :obj:`connection`
        to establish. Also overrides the :meth:`.handle_line` method from :class:`LineReader`
        class with :meth`receive` to provide the possibility to modify the behavior
        of :class:`SerialCommunication` when a new line is received.
        """
        try:
            self._thread.start()
            self.transport, self.protocol = self._thread.connect()
        except Exception as e:
            raise RuntimeError(
                  "Connecting communication thread failed!") from e
        # Assigning methods from pyserial LineReader class to own methods
        self.protocol.handle_line = self.receive
        self.protocol.connection_lost = self.connection_lost

    def disconnect(self):
        """Terminates the connection by stopping :obj:`thread` and further
        closing :obj:`connection`.
        """
        try:
            self._thread.close()
        except Exception as e:
            raise RuntimeError("Connection not closed!") from e

    @property
    def connected(self):
        """Returns the state of :obj:`connection` and :obj:`thread`."""
        return self._serial_connection.is_open and self._thread.is_alive()

    def send(self, text):
        """Sends data to the serial port. If sending fails, exceptions are re-raised
        as :exc:`RuntimeError`.

        :param text: message to be written to the serial port
        :type text: str
        """
        try:
            self.protocol.write_line(text)
        except Exception as e:
            raise RuntimeError("Writing data to serial port failed!") from e

    def receive(self, data):
        """Called when data is received on the serial port.

        .. note:: Method to be overridden by subclassing.
        """
        raise NotImplementedError('Please implement functionality by overriding!')

    def connection_lost(self, e):
        """Called when the connection is closed. If the cause was an error, it is re-raised
        as :exc:`RuntimeError`.

        :param e: Error that caused connection loss
        :type e: Exception
        """
        if isinstance(e, Exception):
            raise RuntimeError("Lost serial connection!") from e

    def __enter__(self):
        """Enter context, connects to the serial port, raises :exc:`RuntimeError` if
        the connection could not be opened.
        """
        self.connect()
        if not self.connected:
            raise RuntimeError("Connection not possible!")
        return self

    def __exit__(self, type, value, traceback):
        """Leave context, disconnect from port."""
        self.disconnect()



if __name__ == '__main__':
    exit(0)
