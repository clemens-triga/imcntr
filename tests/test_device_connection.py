import unittest
from unittest.mock import Mock, patch
from src.imcntr import DeviceConnection
from src.imcntr.device_connection import _SerialLineHandler


class TestDeviceConnection(unittest.TestCase):

    def test_connect_without_port_raises_value_error(self):
        comm = DeviceConnection()
        with self.assertRaises(ValueError):
            comm.connect()

    @patch("serial.threaded.ReaderThread")
    @patch("serial.Serial")
    def test_connect_starts_thread_and_sets_protocol_receiver(self, mock_serial, mock_thread_class):
        # Mock serial instance
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance

        # Mock ReaderThread instance
        mock_thread_instance = Mock()
        mock_protocol = Mock()
        mock_thread_instance.connect.return_value = (Mock(), mock_protocol)
        mock_thread_class.return_value = mock_thread_instance

        comm = DeviceConnection(port="COM1")
        comm.connect()

        mock_serial.assert_called_once_with("COM1")
        mock_thread_class.assert_called_once_with(mock_serial_instance, _SerialLineHandler)
        mock_thread_instance.connect.assert_called_once()
        self.assertEqual(comm._protocol, mock_protocol)
        self.assertEqual(comm._protocol.receiver, comm)
        mock_thread_instance.start.assert_called_once()

    def test_send_calls_protocol_write_line(self):
        comm = DeviceConnection()
        comm._protocol = Mock()
        comm._thread = Mock()
        comm._thread.is_alive.return_value = True
        comm._serial_connection = Mock()
        comm._serial_connection.is_open = True

        comm.send("hello")

        comm._protocol.write_line.assert_called_once_with("hello")

    def test_send_without_connection_raises_runtime_error(self):
        comm = DeviceConnection()
        with self.assertRaises(RuntimeError):
            comm.send("data")

    def test_receive_calls_observer_and_callback(self):
        comm = DeviceConnection()
        callback_mock = Mock()
        comm.receive_callback = callback_mock

        observer_mock = Mock()
        comm._receive_observer.call = observer_mock

        comm.receive("data")

        observer_mock.assert_called_once_with("data")
        callback_mock.assert_called_once_with("data")

    def test_disconnect_closes_thread_and_serial(self):
        comm = DeviceConnection()
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        mock_serial_conn = Mock()
        mock_serial_conn.is_open = True

        comm._thread = mock_thread
        comm._serial_connection = mock_serial_conn

        comm.disconnect()

        mock_thread.close.assert_called_once()
        mock_serial_conn.close.assert_called_once()

    @patch("serial.threaded.ReaderThread")
    @patch("serial.Serial")
    def test_context_manager_connects_and_disconnects(self, mock_serial, mock_thread_class):
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance

        mock_thread_instance = Mock()
        mock_protocol = Mock()
        mock_thread_instance.connect.return_value = (Mock(), mock_protocol)
        mock_thread_instance.is_alive.return_value = True
        mock_thread_class.return_value = mock_thread_instance

        with DeviceConnection(port="COM1") as comm:
            self.assertTrue(comm.connected)
            self.assertEqual(comm._protocol.receiver, comm)

        # Ensure disconnect called on exit
        mock_thread_instance.close.assert_called_once()
        mock_serial_instance.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
