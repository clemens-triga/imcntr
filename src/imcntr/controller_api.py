"""
Controller task definitions and high-level device interfaces.

This module defines controller command/response pairs and provides
high-level interfaces for interacting with the device controller,
sample positioning system, and shutter.

The module builds communication protocol :class:`DeviceConnection` as well as on as
low-level command handlers provided by:class:`SubmitTask` and
:class:`WaitForResponse`, exposing a clear, structured, and type-safe API for
device operation.
"""

from .device_command_handler import WaitForResponse, SubmitTask
from enum import Enum
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TaskDef:
    """
    Represent a task and response pair in form of a `dataclass`.

    :param task: Command string sent to the controller,
                 or ``None`` if the task cannot be submitted.
    :type task: Optional[str]
    :param response: Expected response string from the controller.
    :type response: str
    """
    task: Optional[str]
    response: str


class _Task(Enum):
    """
    Enumeration of controller tasks backed by :class:`TaskDef`.

    Each enum member's *value* is a :class:`TaskDef` instance that defines:

    - ``task``: The command string sent to the controller (or ``None``).
    - ``response``: The expected response string from the controller.
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


class TaskFactory:
    """
    Factory for creating :class:`SubmitTask` and :class:`WaitForResponse`
    instances from :class:`_Task` definitions.

    :param protocol: Communication protocol instance.
    :type protocol: imcntr.device_connection.DeviceConnection
    """

    def __init__(self, protocol):
        self._protocol = protocol

    def submit(self, task):
        """
        Create a :class:`SubmitTask` for a submit-capable controller task.

        :param task: Task enum describing the command and expected response.
        :type task: _Task
        :return: Configured submit task instance.
        :rtype: SubmitTask
        """
        return SubmitTask(
            protocol=self._protocol,
            task=task.value.task,
            response=task.value.response,
        )

    def wait(self, task):
        """
        Create a :class:`WaitForResponse` for a task's expected response.

        :param task: Task enum describing the expected response.
        :type task: _Task
        :return: Configured wait task instance.
        :rtype: WaitForResponse
        """
        return WaitForResponse(
            protocol=self._protocol,
            response=task.value.response,
        )


class Controller:
    """
    Controller interface.

    Provides methods to wait for controller readiness and to check connection
    status.

    :param protocol: Communication protocol instance.
    :type protocol: imcntr.DeviceConnection
    """

    def __init__(self, protocol):
        factory = _TaskFactory(protocol)
        self._ready = factory.wait(_Task.READY)
        self._connected = factory.submit(_Task.CONNECTED)

    def connected(self, timeout):
        """
        Check whether the controller is connected.

        :param timeout: Maximum time to wait for the expected response, in seconds.
        :type timeout: float
        :return: ``True`` if the response is received within the timeout,
                 ``False`` if the timeout expires.
        :rtype: Optional[bool]
        """
        return self._connected(timeout)

    def ready(self, timeout):
        """
        Wait for the controller to report it is ready.

        :param timeout: Maximum time to wait for the ready response, in seconds.
        :type timeout: float
        :return: ``True`` if the controller becomes ready within the timeout,
                 ``False`` otherwise.
        :rtype: bool
        """
        return self._ready(timeout)


class Sample:
    """
    Interface for sample movement and rotation control.

    Provides methods to move sample in/out, rotate, and stop movements.

    :param protocol: Communication protocol instance.
    :type protocol: imcntr.DeviceConnection
    """
    def __init__(self, protocol):
        factory = _TaskFactory(protocol)
        self._move_in = factory.submit(_Task.MOVE_IN)
        self._move_out = factory.submit(_Task.MOVE_OUT)
        self._move_stop = factory.submit(_Task.MOVE_STOP)
        self._rotate_cw = factory.submit(_Task.ROTATE_CW)
        self._rotate_ccw = factory.submit(_Task.ROTATE_CCW)
        self._rotate_stop = factory.submit(_Task.ROTATE_STOP)
        self._stop = factory.submit(_Task.STOP)

    def _validate_step(self, value: int) -> int:
        """
        Validate a rotation step value.

        :param value: Rotation step count.
        :type value: int
        :return: Validated step count.
        :rtype: int
        :raises TypeError: If the value is not an integer.
        :raises ValueError: If the value is not positive.
        """
        if not isinstance(value, int):
            raise TypeError(
                f"Invalid step: must be of type int, got '{type(value).__name__}'"
            )
        if value <= 0:
            raise ValueError(
                f"Invalid step: must be non-zero positive number, got '{value}'"
            )
        return value

    def move_in(self, timeout):
        """
        Move the sample in.

        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        return self._move_in(timeout)

    def move_out(self, timeout):
        """
        Move the sample out.

        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        return self._move_out(timeout)

    def move_stop(self, timeout):
        """
        Stop linear sample movement.

        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        return self._move_stop(timeout)

    def rotate_cw(self, step: int, timeout):
        """
        Rotate the sample clockwise.

        :param step: Number of rotation steps.
        :type step: int
        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        step = self._validate_step(step)
        self._rotate_cw.task = f"{_Task.ROTATE_CW.value.task}+{step}"
        return self._rotate_cw(timeout)

    def rotate_ccw(self, step: int, timeout):
        """
        Rotate the sample counterclockwise.

        :param step: Number of rotation steps.
        :type step: int
        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        step = self._validate_step(step)
        self._rotate_ccw.task = f"{_Task.ROTATE_CCW.value.task}+{step}"
        return self._rotate_ccw(timeout)

    def rotate_stop(self, timeout):
        """
        Stop sample rotation.

        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        return self._rotate_stop(timeout)

    def stop(self, timeout: float):
        """
        Stop all sample movements.

        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        return self._stop(timeout)


class Shutter:
    """
    Interface for shutter control.

    Provides methods to open or close the shutter.

    :param protocol: Communication protocol instance.
    :type protocol: imcntr.DeviceConnection
    """
    def __init__(self, protocol):
        factory = _TaskFactory(protocol)
        self._open = factory.submit(_Task.OPEN)
        self._close = factory.submit(_Task.CLOSE)

    def close(self, timeout: float):
        """
        Close the shutter.

        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        return self._close(timeout)

    def open(self, timeout: float):
        """
        Open the shutter.

        :param timeout: Maximum time to wait for completion, in seconds.
        :type timeout: float
        """
        return self._open(timeout)
