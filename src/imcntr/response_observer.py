class Observer:
    """
    Implements the Observer design pattern.

    This class allows multiple callables (observers) to subscribe to an event source.
    Each observer may be registered with predefined positional and keyword arguments.
    When the event is triggered via :meth:`call`, all subscribed observers are invoked.

    Attributes:
        observers (list): A list of subscribed observers. Each observer is stored as a
        dictionary containing the target callable and its associated arguments.
    """
    def __init__(self):
        """
        Initializes the Observer object with an empty list to hold observers.

        This list will store dictionaries containing the target callable and its associated arguments
        and keyword arguments.
        """
        self._observers = []

    @property
    def observers(self):
        """
        Returns the list of currently subscribed observers.

        :return: List of observer definitions.
        :rtype: list
        """
        return self._observers

    def call(self, *args, **kwargs):
        """
        Invokes all subscribed observers.

        Each observer is called with the arguments provided at subscription time,
        followed by the arguments passed to this method.

        :param args: Additional positional arguments passed to each observer.
        :param kwargs: Additional keyword arguments passed to each observer.
        :raises TypeError: If a TypeError occurs while invoking an observer.
        :raises RuntimeError: If any other exception is raised by an observer.
        """
        for observer in self._observers:
            try:
                # Call the observer's target with its arguments and additional ones passed to call.
                observer['target'](*observer['arguments'], *args, **observer['kwarguments'], **kwargs)
            except TypeError as e:
                # Handle argument mismatch
                raise TypeError("Wrong number of arguments when calling observer!") from e
            except Exception as e:
                # Catch any other exceptions thrown by the observer function
                raise RuntimeError("An exception occurred while calling observer!") from e

    def subscribe(self, target, *args, **kwargs):
        """
        Subscribes a new observer to the subject. The observer is added to the list with any optional arguments
        or keyword arguments provided.

        :param target: The target function or callable to be notified.
        :type target: callable
        :param args: Variable-length argument list that will be passed to the target when called.
        :param kwargs: Arbitrary keyword arguments to be passed to the target when called.
        """
        observer_to_subscribe = {'target': target, 'arguments': args, 'kwarguments': kwargs}

        # Ensure that the observer is not already in the list before adding.
        if observer_to_subscribe not in self._observers:
            self._observers.append(observer_to_subscribe)

    def unsubscribe(self, target=None, *args, remove_all=False, **kwargs):
        """
        Unsubscribes observers from the observer list.

        Behavior depends on the provided arguments:
        - If no target is provided, all observers are removed.
        - If a target is provided and ``remove_all`` is False, only the observer matching
          the target *and* the given arguments is removed.
        - If a target is provided and ``remove_all`` is True, all observers with the given
          target are removed, regardless of their arguments.

        :param target: The observer callable to remove.
        :type target: callable, optional
        :param remove_all: If True, remove all observers matching the target.
        :type remove_all: bool
        :param args: Positional arguments used to match a specific subscription.
        :param kwargs: Keyword arguments used to match a specific subscription.
        """
        if target:
            # If specific target is provided and 'remove_all' is False, remove the observer with matching target and arguments.
            if not remove_all:
                observer_to_unsubscribe = {'target': target, 'arguments': args, 'kwarguments': kwargs}
                if observer_to_unsubscribe in self._observers:
                    self._observers.remove(observer_to_unsubscribe)
            else:
                # If 'remove_all' is True, remove all observers with the matching target.
                for observer in self._observers[:]:
                    if observer['target'] == target:
                        self._observers.remove(observer)
        else:
            # If no target is provided, remove all observers.
            self._observers.clear()
