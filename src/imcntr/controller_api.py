from .device_command_handler import WaitForResponse, SubmitTask
from enum import Enum
from dataclasses import dataclass
from typing import Optional

"""
Imaging Controller Task Interface Module.

This module provides high-level classes and helpers for interacting with an
Imaging controller via a communication protocol. It defines controller tasks,
creates task submission and response-waiting objects, and exposes simple
interfaces for common operations such as moving samples, rotating, stopping
motions, and controlling the shutter.
"""

@dataclass(frozen=True)
class TaskDef:
    """
    Definition of a task and its expected response.

    :param task: The task string to send to the controller. None if the task cannot be submitted.
    :type task: Optional[str]
    :param response: The expected response string from the controller.
    :type response: str
    """
    task: Optional[str]
    response: str


class _Task(Enum):
    """
    Enumeration of controller tasks with their associated definitions.

    Each task contains:
        - `task`: The string to send (if applicable).
        - `response`: The expected response string from the controller.
    """
    READY = TaskDef(None, "controller_ready")
    CONNECTED = TaskDef("connect", "connected")
    OPEN = TaskDef("open_shutter", "shutter_opened")
    CLOSE = TaskDef("close_shutter", "shutter_closed")
    MOVE_OUT = TaskDef("move_out", "pos_out")
    MOVE_IN = TaskDef("move_in", "pos_in")
    MOVE_STOP = TaskDef("stop_lin", "lin_stopped")
    ROTATE_CW = TaskDef("rot_cw", "rot_stopped")
    ROTATE_CCW = TaskDef("rot_ccw", "rot_stopped")
    ROTATE_STOP = TaskDef("stop_rot", "rot_stopped")
    STOP = TaskDef("stop_all", "all_stopped")


class _TaskFactory:
    """
    Factory to create SubmitTask or WaitForResponse instances for controller tasks.
    """

    def __init__(self, protocol):
        """
        Initialize the TaskFactory with a protocol instance.

        :param protocol: Communication protocol instance.
        :type protocol: MessageExchange
        """
        self._protocol = protocol

    def submit(self, task):
        """
        Create a SubmitTask instance for a task that can be submitted.

        :param task: The task enum to submit.
        :type task: _Task
        :return: SubmitTask instance.
        :rtype: SubmitTask
        """
        return SubmitTask(
            protocol=self._protocol,
            task=task.value.task,
            response=task.value.response
        )

    def wait(self, task):
        """
        Create a WaitForResponse instance for a task's expected response.

        :param task: The task enum to wait for.
        :type task: _Task
        :return: WaitForResponse instance.
        :rtype: WaitForResponse
        """
        return WaitForResponse(
            protocol=self._protocol,
            response=task.value.response
        )


class Controller:
    """
    Provides methods to interact with the controller, such as checking readiness and connection.
    """

    def __init__(self, protocol):
        """
        Provides functionality to wait for controller to be ready and check connection.

        :param protocol: Communication protocol instance.
        :type protocol: MessageExchange
        """
        _factory = _TaskFactory(protocol)
        self._ready = _factory.wait(_Task.READY)
        self._connected = _factory.submit(_Task.CONNECTED)

    def connected(self, *args, **kwargs):
        """
        Submit the connect task to the controller.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: True if waiting for response and it is received, None if wait=False.
        :rtype: Optional[bool]
        """
        return self._connected(*args, **kwargs)

    def ready(self, *args, **kwargs):
        """
        Wait for the controller to be ready.

        :param args: Positional arguments forwarded to WaitForResponse.
        :param kwargs: Keyword arguments forwarded to WaitForResponse.
        :return: True if the controller reports ready within the timeout, False otherwise.
        :rtype: bool
        """
        return self._ready(*args, **kwargs)

class Sample:
    """
    Provides functionality to move sample in/out, rotate, and stop movements.
    """

    def __init__(self, protocol):
        """
        Initialize sample movement and rotation tasks.

        :param protocol: Communication protocol instance.
        :type protocol: MessageExchange
        """
        _factory = _TaskFactory(protocol)
        self._move_in = _factory.submit(_Task.MOVE_IN)
        self._move_out = _factory.submit(_Task.MOVE_OUT)
        self._move_stop = _factory.submit(_Task.MOVE_STOP)
        self._rotate_cw = _factory.submit(_Task.ROTATE_CW)
        self._rotate_ccw = _factory.submit(_Task.ROTATE_CCW)
        self._rotate_stop = _factory.submit(_Task.ROTATE_STOP)
        self._stop = _factory.submit(_Task.STOP)

    def _validate_step(self, value):
        """
        Validate that a rotation step is a positive integer.

        Ensures that rotation commands are always sent with a valid positive
        step count to prevent controller errors. Steps must be positive number.

        :param value: Rotation step value.
        :type value: int
        :return: The validated step.
        :rtype: int
        :raises TypeError: If the value is not an int.
        :raises ValueError: If the value is not a positive integer.
        """
        if not isinstance(value, int):
            raise TypeError(f"Invalid step: must be of type int, got '{type(value).__name__}'")
        if value <= 0:
            raise ValueError(f"Invalid step: must be non-zero positive number, got '{value}'")
        return value

    def move_in(self, *args, **kwargs):
        """
        Move the sample in.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        return self._move_in(*args, **kwargs)

    def move_out(self, *args, **kwargs):
        """
        Move the sample out.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        return self._move_out(*args, **kwargs)

    def move_stop(self, *args, **kwargs):
        """
        Stop linear movement of the sample.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        return self._move_stop(*args, **kwargs)

    def rotate_cw(self, step: int, *args, **kwargs):
        """
        Rotate the sample clockwise by a given number of steps.

        Note:
            This method modifies the task string dynamically to include the
            step count.

        :param step: Number of steps to rotate.
        :type step: int
        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        step = self._validate_step(step)
        self._rotate_cw.task = f"{_Task.ROTATE_CW.value.task}+{step}"
        return self._rotate_cw(*args, **kwargs)

    def rotate_ccw(self, step: int, *args, **kwargs):
        """
        Rotate the sample counterclockwise by a given number of steps.

        Note:
            This method modifies the task string dynamically to include the
            step count.

        :param step: Number of steps to rotate.
        :type step: int
        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        step = self._validate_step(step)
        self._rotate_ccw.task = f"{_Task.ROTATE_CCW.value.task}+{step}"
        return self._rotate_ccw(*args, **kwargs)

    def rotate_stop(self, *args, **kwargs):
        """
        Stop rotation of the sample.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        return self._rotate_stop(*args, **kwargs)

    def stop(self, *args, **kwargs):
        """
        Stop all movements of the sample.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        return self._stop(*args, **kwargs)


class Shutter:
    """
    Provides methods to open or close the shutter.
    """

    def __init__(self, protocol):
        """
        Initialize shutter control tasks.

        :param protocol: Communication protocol instance.
        :type protocol: MessageExchange
        """
        _factory = _TaskFactory(protocol)
        self._open = _factory.submit(_Task.OPEN)
        self._close = _factory.submit(_Task.CLOSE)

    def close(self, *args, **kwargs):
        """
        Close the shutter.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        return self._close(*args, **kwargs)

    def open(self, *args, **kwargs):
        """
        Open the shutter.

        :param args: Positional arguments forwarded to SubmitTask.
        :param kwargs: Keyword arguments forwarded to SubmitTask.
        :return: Result from SubmitTask.
        """
        return self._open(*args, **kwargs)

if __name__ == '__main__':
    exit(0)
