import unittest

from assess.decorators.performancedecorator import PerformanceDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import Event, ProcessStartEvent
from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestDistancePerformanceDecorator(unittest.TestCase):
    def test_accumulated_creation(self):
        decorator = PerformanceDecorator()
        self.assertEqual(decorator._name, "accumulated_performance")
        self.assertIsNone(decorator.data())
        self.assertEqual(decorator.descriptive_data(), {
            "accumulated_performance": None
        })

    def test_creation(self):
        decorator = PerformanceDecorator(accumulated=False)
        self.assertEqual(decorator._name, "performance")
        self.assertEqual(decorator.descriptive_data(), {"performance": None})

    def test_decorator(self):
        decorator = PerformanceDecorator(accumulated=False)
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"performance": [[]]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"performance": [[]]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["performance"][0]), 4)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["performance"]), 2)
        self.assertEqual(len(description["performance"][1]), 4)

    def test_accumulated_decorator(self):
        decorator = PerformanceDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {
            "accumulated_performance": [[None]]
        })
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {
            "accumulated_performance": [[None]]
        })

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(type(description["accumulated_performance"][0][0]), float)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["accumulated_performance"]), 2)
        self.assertEqual(type(description["accumulated_performance"][1][0]), float)

    def test_update(self):
        decorator = PerformanceDecorator(accumulated=True)
        decorator._data = [[0.0, 0.0],
                           [0.0, 0.0],
                           [6.919999837875366, 3.8499999046325684],
                           [0.029999999999972715, 0.009999999999990905],
                           [0.05999999999949068, 0.03999999999996362]]
        second_decorator = PerformanceDecorator(accumulated=True)
        second_decorator._data = [[1.0, 1.0],
                                  [0.0, 0.0],
                                  [7.9, 3.8],
                                  [0.03, 0.01],
                                  [0.06, 0.04]]
        decorator.update(second_decorator)
        self.assertEqual(decorator.data(), [[0.0],
                                            [0.0],
                                            [10.769999742507935],
                                            [0.03999999999996362],
                                            [0.0999999999994543],
                                            [2.0],
                                            [0.0],
                                            [11.7],
                                            [0.04],
                                            [0.1]])

        decorator = PerformanceDecorator(accumulated=False)
        decorator._data = [[0.0, 0.0],
                           [0.0, 0.0],
                           [6.919999837875366, 3.8499999046325684],
                           [0.029999999999972715, 0.009999999999990905],
                           [0.05999999999949068, 0.03999999999996362]]
        second_decorator = PerformanceDecorator(accumulated=False)
        second_decorator._data = [[1.0, 1.0],
                                  [0.0, 0.0],
                                  [7.9, 3.8],
                                  [0.03, 0.01],
                                  [0.06, 0.04]]
        decorator.update(second_decorator)
        self.assertEqual(
            decorator.data(), [[0.0, 0.0],
                               [0.0, 0.0],
                               [6.919999837875366, 3.8499999046325684],
                               [0.029999999999972715, 0.009999999999990905],
                               [0.05999999999949068, 0.03999999999996362],
                               [1.0, 1.0],
                               [0.0, 0.0],
                               [7.9, 3.8],
                               [0.03, 0.01],
                               [0.06, 0.04]])
