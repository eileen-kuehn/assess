import unittest

from assess.decorators.decorator import Decorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm


class TestDecorator(unittest.TestCase):
    def test_creation(self):
        decorator = Decorator()
        self.assertIsNone(decorator.algorithm)
        self.assertRaises(NotImplementedError, decorator.data)
        self.assertRaises(NotImplementedError, decorator.descriptive_data)

        algorithm = IncrementalDistanceAlgorithm()
        decorator.wrap_algorithm(algorithm=algorithm)
        self.assertEqual(decorator.algorithm, algorithm)
        self.assertIsNone(decorator.decorator)
        decorator.start_tree()
        decorator.finish_tree()

    def test_chaining(self):
        decorator = Decorator()
        decorator2 = Decorator()
        decorator.decorator = decorator2
        self.assertIsNotNone(decorator.decorator)
        self.assertIsNone(decorator2.decorator)

        algorithm = IncrementalDistanceAlgorithm()
        decorator.algorithm = algorithm
        self.assertEqual(decorator2.algorithm, algorithm)
        decorator.algorithm = None
        decorator.wrap_algorithm(algorithm=algorithm)
        self.assertEqual(decorator2.algorithm, algorithm)
        decorator.start_tree()
        decorator.finish_tree()
