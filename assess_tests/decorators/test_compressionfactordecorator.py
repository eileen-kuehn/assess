import unittest

from assess.decorators.compressionfactordecorator import CompressionFactorDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import Event
from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestCompressionFactorDecorator(unittest.TestCase):
    def test_creation(self):
        decorator = CompressionFactorDecorator()
        self.assertEqual(decorator._name, "compression")
        self.assertIsNone(decorator.data())
        self.assertEqual(
            decorator.descriptive_data(),
            {"compression": None}
        )

    def test_simple_functionality(self):
        decorator = CompressionFactorDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        decorator.wrap_algorithm(algorithm=algorithm)
        decorator.start_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"compression": {
                "prototypes": [],
                "monitoring": [None],
                "accumulated": []
            }}
        )
        decorator.finish_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"compression": {
                "prototypes": [],
                "monitoring": [[0]],
                "accumulated": []
            }}
        )
        algorithm.prototypes = [simple_prototype()]
        decorator.algorithm = algorithm
        decorator.start_tree()
        decorator.finish_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"compression": {
                "prototypes": [[.4]],
                "monitoring": [[0]],
                "accumulated": [.4]
            }}
        )
        decorator.wrap_algorithm(algorithm)
        self.assertEqual(decorator.descriptive_data(), {"compression": None})

    def test_compression_with_events(self):
        decorator = CompressionFactorDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype(), simple_prototype()]
        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"compression": {
                "prototypes": [[.4, .4]],
                "monitoring": [[.25]],
                "accumulated": [.7]
            }}
        )

    def test_update(self):
        decorator = CompressionFactorDecorator()
        decorator._data = {
            "prototypes": [.1, .2, .5],
            "monitoring": [.2],
            "accumulated": .3
        }
        second_decorator = CompressionFactorDecorator()
        second_decorator._data = {
            "prototypes": [.1, .2, .5],
            "monitoring": [.3],
            "accumulated": .3
        }
        decorator.update(second_decorator)
        self.assertEqual(decorator.data(), {
            "prototypes": [.1, .2, .5],
            "monitoring": [.2, .3],
            "accumulated": .3
        })
