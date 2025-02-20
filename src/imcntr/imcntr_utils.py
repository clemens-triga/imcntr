class Observer():
    """
    Implements the Observer design pattern, allowing multiple observers to subscribe to a subject
    and be notified when the subject triggers an event. Observers can subscribe with additional arguments
    or keyword arguments, and the `call` method allows notifying them with specific data.


    """

    def __init__(self):
        """
        Initializes the Observer object with an empty list to hold observers.

        This list will store dictionaries containing the target callable and its associated arguments
        and keyword arguments.
        """
        self.observer = []

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
        if observer_to_subscribe not in self.observer:
            self.observer.append(observer_to_subscribe)

    def subscribe_first(self, target, *args, **kwargs):
        """
        Subscribes a new observer to the subject. The observer is added to the list at the first position with any optional arguments
        or keyword arguments provided.

        :param target: The target function or callable to be notified.
        :type target: callable
        :param args: Variable-length argument list that will be passed to the target when called.
        :param kwargs: Arbitrary keyword arguments to be passed to the target when called.
        """
        observer_to_subscribe = {'target': target, 'arguments': args, 'kwarguments': kwargs}

        # Ensure that the observer is not already in the list before adding.
        if observer_to_subscribe not in self.observer:
            self.observer.insert(0, observer_to_subscribe)

    def unsubscribe(self, target=None, *args, all=False, **kwargs):
        """
        Unsubscribes an observer from the list. Can remove all observers, remove only observers with the exact same
        parameters, or remove all observers of a specific target if `all` is set to True.

        :param target: The target observer to be removed.
        :type target: callable, optional
        :param all: A flag to indicate if all observers of the given target should be removed. Defaults to False.
        :type all: bool
        :param args: Optional arguments that must match the subscribed arguments for removal.
        :param kwargs: Arbitrary keyword arguments to match for removal.
        """
        if target:
            # If specific target is provided and 'all' is False, remove the observer with matching target and arguments.
            if not all:
                observer_to_unsubscribe = {'target': target, 'arguments': args, 'kwarguments': kwargs}
                if observer_to_unsubscribe in self.observer:
                    self.observer.remove(observer_to_unsubscribe)
            else:
                # If 'all' is True, remove all observers with the matching target.
                for observer in self.observer[:]:
                    if observer['target'] == target:
                        self.observer.remove(observer)
        else:
            # If no target is provided, remove all observers.
            self.observer.clear()

    def call(self, *args, **kwargs):
        """
        Calls each subscribed observer with the arguments and keyword arguments passed to `call()`.
        Additionally, observers can be called with their specific arguments that were provided during subscription.

        :param args: Arguments that will be passed to each observer along with its subscribed arguments.
        :param kwargs: Keyword arguments that will be passed to each observer along with its subscribed kwargs.
        :raises RuntimeError: If an error occurs while calling the observer function.
        :raises TypeError: If the number of arguments provided does not match the target function's signature.
        """
        for observer in self.observer:
            try:
                # Call the observer's target with its arguments and additional ones passed to call.
                observer['target'](*observer['arguments'], *args, **observer['kwarguments'], **kwargs)
            except TypeError as e:
                # Handle argument mismatch
                raise TypeError("Wrong number of arguments when calling observer!") from e
            except Exception as e:
                # Catch any other exceptions thrown by the observer function
                raise RuntimeError("An exception occurred while calling observer!") from e

if __name__ == '__main__':
    exit(0)
