import unittest
from unittest.mock import MagicMock, patch

from src.imcntr import Controller, Sample, Shutter
from src.imcntr.controller_api import _Task, _TaskFactory


class TestController(unittest.TestCase):
    def setUp(self):
        self.protocol = MagicMock()
        patcher = patch('src.imcntr.controller_api._TaskFactory')
        self.addCleanup(patcher.stop)
        self.mock_factory_cls = patcher.start()
        self.mock_factory = self.mock_factory_cls.return_value

        # Mock submit and wait methods
        self.mock_submit = MagicMock()
        self.mock_wait = MagicMock()
        self.mock_factory.submit.side_effect = lambda task: self.mock_submit
        self.mock_factory.wait.side_effect = lambda task: self.mock_wait

    def test_controller_ready_and_connected_calls_correct_task(self):
        controller = Controller(self.protocol)
        # ready should call wait for READY
        controller.ready()
        self.mock_factory.wait.assert_any_call(_Task.READY)
        self.mock_wait.assert_called_once()

        # connected should call submit for CONNECTED
        controller.connected()
        self.mock_factory.submit.assert_any_call(_Task.CONNECTED)
        self.mock_submit.assert_called_once()


class TestSample(unittest.TestCase):
    def setUp(self):
        self.protocol = MagicMock()
        patcher = patch('src.imcntr.controller_api._TaskFactory')
        self.addCleanup(patcher.stop)
        self.mock_factory_cls = patcher.start()
        self.mock_factory = self.mock_factory_cls.return_value

        # Create mock SubmitTask for all sample tasks
        self.mock_submit = MagicMock()
        self.mock_factory.submit.side_effect = lambda task: self.mock_submit

        self.sample = Sample(self.protocol)

    def test_move_in_calls_correct_task(self):
        self.sample.move_in()
        self.mock_factory.submit.assert_any_call(_Task.MOVE_IN)
        self.mock_submit.assert_called_once()

    def test_move_out_calls_correct_task(self):
        self.sample.move_out()
        self.mock_factory.submit.assert_any_call(_Task.MOVE_OUT)
        self.mock_submit.assert_called_once()

    def test_move_stop_calls_correct_task(self):
        self.sample.move_stop()
        self.mock_factory.submit.assert_any_call(_Task.MOVE_STOP)
        self.mock_submit.assert_called_once()

    def test_rotate_cw_calls_correct_task_and_validates_step(self):
        self.sample.rotate_cw(5)
        self.mock_factory.submit.assert_any_call(_Task.ROTATE_CW)
        self.mock_submit.assert_called_once()
        with self.assertRaises(TypeError):
            self.sample.rotate_cw("invalid")
        with self.assertRaises(ValueError):
            self.sample.rotate_cw(0)

    def test_rotate_ccw_calls_correct_task_and_validates_step(self):
        self.sample.rotate_ccw(3)
        self.mock_factory.submit.assert_any_call(_Task.ROTATE_CCW)
        self.mock_submit.assert_called_once()
        with self.assertRaises(TypeError):
            self.sample.rotate_ccw(3.5)
        with self.assertRaises(ValueError):
            self.sample.rotate_ccw(-1)

    def test_rotate_stop_calls_correct_task(self):
        self.sample.rotate_stop()
        self.mock_factory.submit.assert_any_call(_Task.ROTATE_STOP)
        self.mock_submit.assert_called_once()

    def test_stop_calls_correct_task(self):
        self.sample.stop()
        self.mock_factory.submit.assert_any_call(_Task.STOP)
        self.mock_submit.assert_called_once()


class TestShutter(unittest.TestCase):
    def setUp(self):
        self.protocol = MagicMock()
        patcher = patch('src.imcntr.controller_api._TaskFactory')
        self.addCleanup(patcher.stop)
        self.mock_factory_cls = patcher.start()
        self.mock_factory = self.mock_factory_cls.return_value

        self.mock_submit = MagicMock()
        self.mock_factory.submit.side_effect = lambda task: self.mock_submit

        self.shutter = Shutter(self.protocol)

    def test_open_calls_correct_task(self):
        self.shutter.open()
        self.mock_factory.submit.assert_any_call(_Task.OPEN)
        self.mock_submit.assert_called_once()

    def test_close_calls_correct_task(self):
        self.shutter.close()
        self.mock_factory.submit.assert_any_call(_Task.CLOSE)
        self.mock_submit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
