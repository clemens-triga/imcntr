class Observer():
    """Implements the observer design pattern by providing a list where observers can subscribe and get called when the subject of interest notifies them.
    """
    def __init__(self):
        self.observer = []

    def subscribe(self, target, *args, **kwargs):
        """Appends target with optional arguments or keyword arguments
        to the observer list.

        :param target: Tartget to be called from subject.
        :type port: callable
        :param args: Variable length argument list, passed to the target when called
        :param kwargs: Arbitrary keyword arguments, passed to the target when called
        """
        observer_to_subscribe = {'target' : target, 'arguments' : args, 'kwarguments' : kwargs}
        if observer_to_subscribe  not in self.observer:
            self.observer.append(observer_to_subscribe)

    def unsubscribe(self, target = None, *args, all = False, **kwargs):
        """Remove observer from list. If no :obj:`target` is given all observers are removed, if :obj:`all` is true all observers with same :obj:`target` are removed. Otherwise :obj:`target`, :obj:`*args` and :obj:`**kwargs` musst be the same as subscribing.

        :param target: Tartget object of observed subject.
        :type port: callable
        :param all: Specifies if all observer with same :obj:`target` are removed from list
        :type all: bool
        :param args: Variable length argument list, passed to the target when called
        :param kwargs: Arbitrary keyword arguments, passed to the target when called
        """
        if target:
            if not all:
                obersver_to_unsubscribe={'target' : target, 'arguments' : args, 'kwarguments' : kwargs}
                if obersver_to_unsubscribe in self.observer:
                    self.observer.remove(obersver_to_unsubscribe)
            else:
                for observer in self.observer[:]:
                    if observer['target'] == target:
                        self.observer.remove(observer)
        else:
            for observer in self.observer[:]:
                self.observer.remove(observer)

    def call(self, *args, **kwargs):
        """alls each target with its arguments and keyword arguments in observer list. Also provides the possibility to pass over own arguments to the callable tartget.

        :raise RuntimeError: Some other exception occured during call of observer
        :raise TypeError: Number of required arguments don't match passed arguments
        """
        for observer in self.observer:
            try:
                observer['target'](*observer['arguments'], *args, **observer['kwarguments'], **kwargs)
            except TypeError as e:
                raise TypeError("Wrong number of arguments when calling observer!") from e
            except Exception as e:
                raise RuntimeError("Some Exception occured during observer call") from e

if __name__ == '__main__':
    exit(0)
