import unittest

from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import Event
from assess.exceptions.exceptions import MatrixDoesNotMatchBounds
from assess_tests.basedata import simple_prototype, simple_monitoring_tree, \
    simple_additional_monitoring_tree


class TestDistanceMatrixDecorator(unittest.TestCase):
    def test_creation(self):
        decorator = DistanceMatrixDecorator()
        self.assertEqual(decorator._name, "matrix")
        self.assertIsNone(decorator.data())
        self.assertEqual(
            decorator.descriptive_data(),
            {"matrix": None}
        )

    def test_normalized_creation(self):
        decorator = DistanceMatrixDecorator(normalized=True)
        self.assertEqual(decorator._name, "normalized_matrix")
        self.assertEqual(
            decorator.descriptive_data(),
            {"normalized_matrix": None}
        )

    def test_simple_matrix(self):
        decorator = DistanceMatrixDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"matrix": [[]]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"matrix": [[]]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_prototype()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"matrix": [[0]]})

        algorithm.prototypes = [simple_prototype(), simple_additional_monitoring_tree()]
        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_prototype()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"matrix": [[0, 2]]})
        decorator.start_tree()
        for event in Event.from_tree(simple_additional_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"matrix": [[0, 2], [2, 0]]})
        self.assertRaises(MatrixDoesNotMatchBounds, decorator.start_tree)

    def test_simple_normalized_matrix(self):
        decorator = DistanceMatrixDecorator(normalized=True)
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"normalized_matrix": [[]]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"normalized_matrix": [[]]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_prototype()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"normalized_matrix": [[0]]})

        algorithm.prototypes = [simple_prototype(), simple_additional_monitoring_tree()]
        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_prototype()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"normalized_matrix": [[0, .25]]})
        decorator.start_tree()
        for event in Event.from_tree(simple_additional_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"normalized_matrix": [[0, .25], [.25, 0]]})
        self.assertRaises(MatrixDoesNotMatchBounds, decorator.start_tree)
