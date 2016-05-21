import unittest

from assess.decorators.signatureperformancedecorator import SignaturePerformanceDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import Event
from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestDistancePerformanceDecorator(unittest.TestCase):
    def test_accumulated_creation(self):
        decorator = SignaturePerformanceDecorator()
        self.assertEqual(decorator._name, "accumulated_signature_performance")
        self.assertIsNone(decorator.data())
        self.assertEqual(decorator.descriptive_data(), {"accumulated_signature_performance": None})

    def test_creation(self):
        decorator = SignaturePerformanceDecorator(accumulated=False)
        self.assertEqual(decorator._name, "signature_performance")
        self.assertEqual(decorator.descriptive_data(), {"signature_performance": None})

    def test_decorator(self):
        decorator = SignaturePerformanceDecorator(accumulated=False)
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"signature_performance": [{}]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"signature_performance": [{}]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["signature_performance"][0]), 5)
        self.assertEqual(len(description["signature_performance"][0]["user time"]), 4)
        self.assertEqual(len(description["signature_performance"][0]["system time"]), 4)
        self.assertEqual(len(description["signature_performance"][0]["children's user time"]), 4)
        self.assertEqual(len(description["signature_performance"][0]["children's system time"]), 4)
        self.assertEqual(len(description["signature_performance"][0]["elapsed real time"]), 4)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["signature_performance"]), 2)
        self.assertEqual(len(description["signature_performance"][1]["user time"]), 4)
        self.assertEqual(len(description["signature_performance"][1]["system time"]), 4)
        self.assertEqual(len(description["signature_performance"][1]["children's user time"]), 4)
        self.assertEqual(len(description["signature_performance"][1]["children's system time"]), 4)
        self.assertEqual(len(description["signature_performance"][1]["elapsed real time"]), 4)

    def test_accumulated_decorator(self):
        decorator = SignaturePerformanceDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"accumulated_signature_performance": [{}]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"accumulated_signature_performance": [{}]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(type(description["accumulated_signature_performance"][0]["user time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][0]["system time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][0]["children's user time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][0]["children's system time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][0]["elapsed real time"]), float)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["accumulated_signature_performance"]), 2)
        self.assertEqual(type(description["accumulated_signature_performance"][1]["user time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][1]["system time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][1]["children's user time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][1]["children's system time"]), float)
        self.assertEqual(type(description["accumulated_signature_performance"][1]["elapsed real time"]), float)
