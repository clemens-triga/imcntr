from .imcntr_communication import WaitForResponse, GiveOrder

class Ready(WaitForResponse):
    """
    Waits for the response `"controller_ready"`. Message indicates a successful startup.

    :param args: Arguments passed to the parent :class:`WaitForResponse` class.
    :param kwargs: Keyword arguments passed to the parent class:`WaitForResponse` class.
    """
    def __init__(self, *args, **kwargs):
        response = "controller_ready"
        super(Ready, self).__init__(*args, response = response, **kwargs)


class Connected(GiveOrder):
    """
    Issues `"connect"` order to check if controller is successfully connectedgives possibility and wait for response `"connected"`.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "connect"
        response = "connected"
        super(Connected, self).__init__(*args, order = order, response = response, **kwargs)


class Out(GiveOrder):
    """
    Issues `"move_out"` order to move sample out and gives possibility to wait for response `"pos_out"` after movement is finished.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "move_out"
        response = "pos_out"
        super(Out, self).__init__(*args, order = order, response = response, **kwargs)


class In(GiveOrder):
    """
    Issues `"move_in"` order to move sample in and gives possibility to wait for response `"pos_in"` after movement is finished.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "move_in"
        response = "pos_in"
        super(In, self).__init__(*args, order = order, response =  response, **kwargs)


class Clockwise(GiveOrder):
    """
    Issues  `"rot_cw+STEPS"` order to rotate sample clockwise by given number of steps. Gives possibility to wait for response `"rot_stopped"` after rotation is finished.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, steps = 0, **kwargs):
        order = "rot_cw" + "+" + str(steps)
        response = "rot_stopped"
        super(Clockwise, self).__init__(*args, order = order, response = response, **kwargs)


    def __call__(self, steps = None):
        """
        If steps are given, adds the number of steps to the rotation order and sends it to the controller. If no steps are given

        :param steps: The number of steps to rotate sample clockwise.
        :type steps: int
        """
        if steps:
            order = self.order.split('+',1)[0] + "+" + str(steps)
            super(Clockwise, self).__call__(order)
        else:
            super(Clockwise, self).__call__()


class CounterClockwise(Clockwise):
    """
    Issues `"rot_ccw+STEPS"` order to rotate sample clockwise by given number of steps. Gives possibility to wait for response `"rot_stopped"` after rotation is finished.

    :param args: Arguments passed to parent :class:`Clockwise` class.
    :param kwargs: Keyword arguments passed to parent :class:`Clockwise` class.
    """

    def __init__(self, *args, steps = 0, **kwargs):
        order = "rot_ccw" + "+" + str(steps)
        response = "rot_stopped"
        super(Clockwise, self).__init__(*args, order = order, response = response, **kwargs)


class Open(GiveOrder):
    """
    Issues `"open_shutter"` order to open shutter and gives possibility to wait for response `"shutter_opened"` after shutter is opened.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "open_shutter"
        response = "shutter_opened"
        super(Open, self).__init__(*args, order = order, response =  response, **kwargs)


class Close(GiveOrder):
    """
    Issues `"close_shutter"` order to close shutter and gives possibility to wait for response `"shutter_closed"` after shutter is closed.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "close_shutter"
        response = "shutter_closed"
        super(Close, self).__init__(*args, order = order, response =  response, **kwargs)


class StopMove(GiveOrder):
    """
    Issues `"stop_lin"` order to stop linear movement and gives possibility to wait for response `"lin_stopped"` after stop.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "stop_lin"
        response = "lin_stopped"
        super(StopMove, self).__init__(*args, order = order, response =  response, **kwargs)


class StopRotate(GiveOrder):
    """
    Issues `"stop_rot"` order to stop rotational movement and gives possibility to wait for response `"rot_stopped"` after stop.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "stop_rot"
        response = "rot_stopped"
        super(StopRotate, self).__init__(*args, order = order, response =  response, **kwargs)


class Stop(GiveOrder):
    """
    Issues `"stop_all"` order to stop all movement and gives possibility to wait for response `"all_stopped"` after stop.

    :param args: Arguments passed to parent :class:`GiveOrder` class.
    :param kwargs: Keyword arguments passed to parent :class:`GiveOrder` class.
    """
    def __init__(self, *args, **kwargs):
        order = "stop_all"
        response = "all_stopped"
        super(Stop, self).__init__(*args, order = order, response =  response, **kwargs)


class Controller():
    """
    Provides methods to interact with the controller, such as checking if it's ready and connected.

    :ivar ready: The instance for checking if the controller is ready.
    :type ready: :class:`Ready`
    :ivar connected: The instance for checking if the controller is connected.
    :type connected: :class:`Connected`
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the controller and checks readiness and connection.

        :param args: Arguments passed to the :class:`Ready` and :class:`Connected` classes.
        :param kwargs: Keyword arguments passed to the :class:`Ready` and :class:`Connected` classes.
        """
        self.ready = Ready(*args, **kwargs)
        self.connected = Connected(*args, **kwargs)


class Sample():
    """
    Provides functionality to move sample in or out, rotate, and stop movements.

    :ivar move_out: The instance for moving sample out.
    :type move_out: :class:`Out`
    :ivar move_in: The instance for moving sample in.
    :type move_in: :class:`In`
    :ivar move_stop: The instance for stopping linear movement.
    :type move_stop: :class:`StopMove`
    :ivar rotate_cw: The instance for rotating sample clockwise.
    :type rotate_cw: :class:`Clockwise`
    :ivar rotate_ccw: The instance for rotating sample counterclockwise.
    :type rotate_ccw: :class:`CounterClockwise`
    :ivar rotate_stop: The instance for stopping rotational movement.
    :type rotate_stop: :class:`StopRotate`
    :ivar stop: The instance for stopping all movements.
    :type stop: :class:`Stop`
    """

    def __init__(self, *args, **kwargs):
        self.move_out = Out(*args, **kwargs)
        self.move_in = In(*args, **kwargs)
        self.move_stop = StopMove(*args, **kwargs)
        self.rotate_cw = Clockwise(*args, **kwargs)
        self.rotate_ccw = CounterClockwise(*args, **kwargs)
        self.rotate_stop = StopRotate(*args, **kwargs)
        self.stop = Stop(*args, **kwargs)


class Shutter():
    """
    Provides methods to open or close the shutter.

    :ivar open: The instance for opening shutter.
    :type open: :class:`Open`
    :ivar close: The instance for closing shutter.
    :type close: :class:`Close`
    """

    def __init__(self, *args, **kwargs):
        self.open = Open(*args, **kwargs)
        self.close = Close(*args, **kwargs)


if __name__ == '__main__':
    exit(0)
