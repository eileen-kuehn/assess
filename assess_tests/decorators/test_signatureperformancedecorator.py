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
        self.assertEqual(decorator.descriptive_data(), {"signature_performance": {
            "user time": [[]],
            "system time": [[]],
            "children's user time": [[]],
            "children's system time": [[]],
            "elapsed real time": [[]]
        }})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"signature_performance": {
            "user time": [[]],
            "system time": [[]],
            "children's user time": [[]],
            "children's system time": [[]],
            "elapsed real time": [[]]
        }})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["signature_performance"].keys()), 5)
        self.assertEqual(len(description["signature_performance"]["user time"][0]), 4)
        self.assertEqual(len(description["signature_performance"]["system time"][0]), 4)
        self.assertEqual(len(description["signature_performance"]["children's user time"][0]), 4)
        self.assertEqual(len(description["signature_performance"]["children's system time"][0]), 4)
        self.assertEqual(len(description["signature_performance"]["elapsed real time"][0]), 4)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["signature_performance"]["user time"]), 2)
        self.assertEqual(len(description["signature_performance"]["user time"][1]), 4)
        self.assertEqual(len(description["signature_performance"]["system time"][1]), 4)
        self.assertEqual(len(description["signature_performance"]["children's user time"][1]), 4)
        self.assertEqual(len(description["signature_performance"]["children's system time"][1]), 4)
        self.assertEqual(len(description["signature_performance"]["elapsed real time"][1]), 4)

    def test_accumulated_decorator(self):
        decorator = SignaturePerformanceDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"accumulated_signature_performance": {
            "user time": [[]],
            "system time": [[]],
            "children's user time": [[]],
            "children's system time": [[]],
            "elapsed real time": [[]]
        }})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"accumulated_signature_performance": {
            "user time": [[]],
            "system time": [[]],
            "children's user time": [[]],
            "children's system time": [[]],
            "elapsed real time": [[]]
        }})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(type(description["accumulated_signature_performance"]["user time"][0][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["system time"][0][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["children's user time"][0][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["children's system time"][0][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["elapsed real time"][0][0]), float)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["accumulated_signature_performance"]["user time"]), 2)
        self.assertEqual(type(description["accumulated_signature_performance"]["user time"][1][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["system time"][1][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["children's user time"][1][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["children's system time"][1][0]), float)
        self.assertEqual(type(description["accumulated_signature_performance"]["elapsed real time"][1][0]), float)

    def test_update(self):
        decorator = SignaturePerformanceDecorator(accumulated=True)
        decorator._data = {
            "children's system time": [[0.0, 0.0]],
            "children's user time": [[0.0, 0.0]],
            'elapsed real time': [[6.919999837875366, 3.8499999046325684]],
            'system time': [[0.029999999999972715, 0.009999999999990905]],
            'user time': [[0.05999999999949068, 0.03999999999996362]]
        }
        second_decorator = SignaturePerformanceDecorator(accumulated=True)
        second_decorator._data = {
            "children's system time": [[1.0, 1.0]],
            "children's user time": [[0.0, 0.0]],
            'elapsed real time': [[7.9, 3.8]],
            'system time': [[0.03, 0.01]],
            'user time': [[0.06, 0.04]]
        }
        decorator.update(second_decorator)
        self.assertEqual(decorator.data(), {
            "children's system time": [[0.0],[2.0]],
            "children's user time": [[0.0],[0.0]],
            'elapsed real time': [[10.769999742507935],[11.7]],
            'system time': [[0.03999999999996362],[0.04]],
            'user time': [[0.0999999999994543],[0.1]]
        })

        decorator = SignaturePerformanceDecorator(accumulated=False)
        decorator._data = {
            "children's system time": [[0.0, 0.0]],
            "children's user time": [[0.0, 0.0]],
            'elapsed real time': [[6.919999837875366, 3.8499999046325684]],
            'system time': [[0.029999999999972715, 0.009999999999990905]],
            'user time': [[0.05999999999949068, 0.03999999999996362]]
        }
        second_decorator = SignaturePerformanceDecorator(accumulated=False)
        second_decorator._data = {
            "children's system time": [[1.0, 1.0]],
            "children's user time": [[0.0, 0.0]],
            'elapsed real time': [[7.9, 3.8]],
            'system time': [[0.03, 0.01]],
            'user time': [[0.06, 0.04]]
        }
        decorator.update(second_decorator)
        self.assertEqual(decorator.data(), {
            "children's system time": [[0.0, 0.0], [1.0, 1.0]],
            "children's user time": [[0.0, 0.0], [0.0, 0.0]],
            'elapsed real time': [[6.919999837875366, 3.8499999046325684], [7.9, 3.8]],
            'system time': [[0.029999999999972715, 0.009999999999990905], [0.03, 0.01]],
            'user time': [[0.05999999999949068, 0.03999999999996362], [0.06, 0.04]]
        })
