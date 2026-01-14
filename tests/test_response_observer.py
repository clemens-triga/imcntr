import unittest
from src.imcntr import Observer

class TestObserver(unittest.TestCase):

    def setUp(self):
        self.observer = Observer()
        self.callback_calls = []

    def dummy_callback(self, *args, **kwargs):
        self.callback_calls.append((args, kwargs))

    def test_subscribe_and_call(self):
        self.observer.subscribe(self.dummy_callback, 1, 2, key="value")
        self.observer.call(3, 4, extra="test")
        self.assertEqual(self.callback_calls, [((1, 2, 3, 4), {'key': 'value', 'extra': 'test'})])

    def test_unsubscribe_specific(self):
        self.observer.subscribe(self.dummy_callback, 1)
        self.observer.unsubscribe(self.dummy_callback, 1)
        self.assertEqual(self.observer.observers, [])

    def test_unsubscribe_all_for_target(self):
        self.observer.subscribe(self.dummy_callback, 1)
        self.observer.subscribe(self.dummy_callback, 2)
        self.observer.unsubscribe(self.dummy_callback, remove_all=True)
        self.assertEqual(self.observer.observers, [])

    def test_unsubscribe_all_without_target(self):
        self.observer.subscribe(self.dummy_callback, 1)
        self.observer.unsubscribe()
        self.assertEqual(self.observer.observers, [])

    def test_call_type_error(self):
        def callback_no_args():
            pass
        self.observer.subscribe(callback_no_args)
        with self.assertRaises(TypeError):
            self.observer.call(1)

    def test_call_runtime_error(self):
        def callback_raises():
            raise ValueError("Oops")
        self.observer.subscribe(callback_raises)
        with self.assertRaises(RuntimeError):
            self.observer.call()

if __name__ == "__main__":
    unittest.main()
