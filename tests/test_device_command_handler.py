import unittest
from unittest.mock import patch, Mock
import threading
import time

from src.imcntr import WaitForResponse, SubmitTask

class MockObserver:
    """Minimal observer implementation for testing."""
    def __init__(self):
        self._callbacks = []

    def subscribe(self, callback):
        self._callbacks.append(callback)

    def unsubscribe(self, callback):
        self._callbacks.remove(callback)

    def call(self, data):
        for cb in list(self._callbacks):
            cb(data)

class TestWaitForResponse(unittest.TestCase):

    def setUp(self):
        self.observer = MockObserver()
        self.protocol = Mock()
        self.protocol.send = Mock()
        self.protocol.receive_observer = self.observer

    def test_wait_success(self):
        waiter = WaitForResponse(self.protocol, response="OK", timeout=1)
        def delayed_call():
            time.sleep(0.05)
            self.observer.call("OK")

        threading.Thread(target=delayed_call).start()

        result = waiter()

        self.assertTrue(result)

    def test_wait_timeout(self):
        waiter = WaitForResponse(self.protocol, response="OK", timeout=0.05)

        result = waiter()

        self.assertFalse(result)

    def test_subscribe_and_unsubscribe(self):
        waiter = WaitForResponse(self.protocol, response="OK", timeout=0.01)

        waiter()

        self.assertEqual(len(self.observer._callbacks), 0)

    def test_call_without_response_raises(self):
        waiter = WaitForResponse(self.protocol)
        with self.assertRaises(ValueError):
            waiter()

    def test_invalid_signal_type(self):
        with self.assertRaises(TypeError):
            WaitForResponse(self.protocol, response=123)
        task = SubmitTask(self.protocol, response="OK", task="CMD")
        with self.assertRaises(TypeError):
            task.task = 456

    def test_invalid_timeout(self):
        with self.assertRaises(TypeError):
            WaitForResponse(self.protocol, response="OK", timeout="abc")
        with self.assertRaises(ValueError):
            WaitForResponse(self.protocol, response="OK", timeout=-1)

    def test_multiple_emissions(self):
        waiter = WaitForResponse(self.protocol, response="OK", timeout=1)

        def emit_multiple():
            for _ in range(3):
                time.sleep(0.01)
                self.observer.call("OK")

        threading.Thread(target=emit_multiple).start()
        result = waiter()
        self.assertTrue(result)
        # Ensure no callbacks remain after wait
        self.assertEqual(len(self.observer._callbacks), 0)



class TestSubmitTask(unittest.TestCase):

    def setUp(self):
        self.observer = MockObserver()
        self.protocol = Mock()
        self.protocol.send = Mock()
        self.protocol.receive_observer = self.observer

    def test_send_without_wait(self):
        task = SubmitTask(
            self.protocol,
            response="OK",
            task="CMD",
            timeout=1
        )

        result = task(wait=False)

        self.protocol.send.assert_called_once_with("CMD")
        self.assertIsNone(result)

    def test_send_and_wait_success(self):
        task = SubmitTask(
            self.protocol,
            response="OK",
            task="CMD",
            timeout=1
        )

        def delayed_call():
            time.sleep(0.05)
            self.observer.call("OK")

        threading.Thread(target=delayed_call).start()

        result = task(wait=True)

        self.protocol.send.assert_called_once_with("CMD")
        self.assertTrue(result)

    def test_send_and_wait_timeout(self):
        task = SubmitTask(
            self.protocol,
            response="OK",
            task="CMD",
            timeout=0.05
        )

        result = task(wait=True)

        self.protocol.send.assert_called_once_with("CMD")
        self.assertFalse(result)

    def test_task_override(self):
        task = SubmitTask(
            self.protocol,
            response="OK",
            task="DEFAULT",
            timeout=1
        )
        task.task = "CUSTOM"

        task(wait=False)

        self.protocol.send.assert_called_once_with("CUSTOM")

    def test_submit_task_no_task_raises(self):
        task = SubmitTask(self.protocol, response="OK")
        with self.assertRaises(ValueError):
            task(wait=False)

    def test_submit_task_custom_timeout(self):
        task = SubmitTask(self.protocol, response="OK", task="CMD", timeout=1)

        def delayed_call():
            time.sleep(0.05)
            self.observer.call("OK")

        threading.Thread(target=delayed_call).start()
        result = task(timeout=0.1, wait=True)
        self.assertTrue(result)



if __name__ == "__main__":
    unittest.main()
