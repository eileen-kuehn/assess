import unittest

from assess.decorators.decorator import Decorator
from assess.decorators.compressionfactordecorator import CompressionFactorDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.exceptions.exceptions import DecoratorNotFoundException
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator


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

    def test_update(self):
        decorator = Decorator()
        second_decorator = Decorator()
        decorator.update(second_decorator)

        decorator = Decorator()
        second_decorator.decorator = CompressionFactorDecorator()
        self.assertRaises(DecoratorNotFoundException, decorator.update, second_decorator)

    def test_decorator_from_name(self):
        decorator = Decorator.from_name("matrix")
        print(decorator)
        self.assertEqual(decorator.__class__, DistanceMatrixDecorator)
