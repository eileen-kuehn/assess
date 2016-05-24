import unittest

from assess.decorators.distanceperformancedecorator import DistancePerformanceDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import Event
from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestDistancePerformanceDecorator(unittest.TestCase):
    def test_accumulated_creation(self):
        decorator = DistancePerformanceDecorator()
        self.assertEqual(decorator._name, "accumulated_distance_performance")
        self.assertIsNone(decorator.data())
        self.assertEqual(decorator.descriptive_data(), {"accumulated_distance_performance": None})

    def test_creation(self):
        decorator = DistancePerformanceDecorator(accumulated=False)
        self.assertEqual(decorator._name, "distance_performance")
        self.assertEqual(decorator.descriptive_data(), {"distance_performance": None})

    def test_decorator(self):
        decorator = DistancePerformanceDecorator(accumulated=False)
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"distance_performance": [{}]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"distance_performance": [{}]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["distance_performance"][0]), 5)
        self.assertEqual(len(description["distance_performance"][0]["user time"]), 4)
        self.assertEqual(len(description["distance_performance"][0]["system time"]), 4)
        self.assertEqual(len(description["distance_performance"][0]["children's user time"]), 4)
        self.assertEqual(len(description["distance_performance"][0]["children's system time"]), 4)
        self.assertEqual(len(description["distance_performance"][0]["elapsed real time"]), 4)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["distance_performance"]), 2)
        self.assertEqual(len(description["distance_performance"][1]["user time"]), 4)
        self.assertEqual(len(description["distance_performance"][1]["system time"]), 4)
        self.assertEqual(len(description["distance_performance"][1]["children's user time"]), 4)
        self.assertEqual(len(description["distance_performance"][1]["children's system time"]), 4)
        self.assertEqual(len(description["distance_performance"][1]["elapsed real time"]), 4)

    def test_accumulated_decorator(self):
        decorator = DistancePerformanceDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"accumulated_distance_performance": [{}]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"accumulated_distance_performance": [{}]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(type(description["accumulated_distance_performance"][0]["user time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][0]["system time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][0]["children's user time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][0]["children's system time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][0]["elapsed real time"]), float)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["accumulated_distance_performance"]), 2)
        self.assertEqual(type(description["accumulated_distance_performance"][1]["user time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][1]["system time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][1]["children's user time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][1]["children's system time"]), float)
        self.assertEqual(type(description["accumulated_distance_performance"][1]["elapsed real time"]), float)

    def test_update(self):
        decorator = DistancePerformanceDecorator()
        decorator._performances = [{
            "children's system time": [0.0, 0.0],
            "children's user time": [0.0, 0.0],
            'elapsed real time': [6.919999837875366, 3.8499999046325684],
            'system time': [0.029999999999972715, 0.009999999999990905],
            'user time': [0.05999999999949068, 0.03999999999996362]
        }]
        second_decorator = DistancePerformanceDecorator()
        second_decorator._performances = [{
            "children's system time": [1.0, 1.0],
            "children's user time": [0.0, 0.0],
            'elapsed real time': [7.9, 3.8],
            'system time': [0.03, 0.01],
            'user time': [0.06, 0.04]
        }]
        decorator.update(second_decorator)
        self.assertEqual(decorator.data(), [{
            "children's system time": 0.0,
            "children's user time": 0.0,
            'elapsed real time': 10.769999742507935,
            'system time': 0.03999999999996362,
            'user time': 0.0999999999994543
        }, {
            "children's system time": 2.0,
            "children's user time": 0.0,
            'elapsed real time': 11.7,
            'system time': 0.04,
            'user time': 0.1
        }])

        decorator = DistancePerformanceDecorator(accumulated=False)
        decorator._performances = [{
            "children's system time": [0.0, 0.0],
            "children's user time": [0.0, 0.0],
            'elapsed real time': [6.919999837875366, 3.8499999046325684],
            'system time': [0.029999999999972715, 0.009999999999990905],
            'user time': [0.05999999999949068, 0.03999999999996362]
        }]
        second_decorator = DistancePerformanceDecorator(accumulated=False)
        second_decorator._performances = [{
            "children's system time": [1.0, 1.0],
            "children's user time": [0.0, 0.0],
            'elapsed real time': [7.9, 3.8],
            'system time': [0.03, 0.01],
            'user time': [0.06, 0.04]
        }]
        decorator.update(second_decorator)
        self.assertEqual(decorator.data(), [{
            "children's system time": [0.0, 0.0],
            "children's user time": [0.0, 0.0],
            'elapsed real time': [6.919999837875366, 3.8499999046325684],
            'system time': [0.029999999999972715, 0.009999999999990905],
            'user time': [0.05999999999949068, 0.03999999999996362]
        }, {
            "children's system time": [1.0, 1.0],
            "children's user time": [0.0, 0.0],
            'elapsed real time': [7.9, 3.8],
            'system time': [0.03, 0.01],
            'user time': [0.06, 0.04]
        }])
