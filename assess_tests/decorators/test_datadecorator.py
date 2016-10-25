import unittest

from assess.decorators.datadecorator import DataDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import Event
from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestDataDecorator(unittest.TestCase):
    def test_creation(self):
        decorator = DataDecorator()
        self.assertEqual(decorator._name, "data")
        self.assertIsNone(decorator.data())
        self.assertEqual(
            decorator.descriptive_data(),
            {"data": None}
        )

    def test_decorator(self):
        decorator = DataDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"data": {
                "prototypes": {
                    "original": [[5]],
                    "converted": [[3]]
                },
                "monitoring": {}
            }}
        )
        decorator.finish_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"data": {
                "prototypes": {
                    "original": [[5]],
                    "converted": [[3]]
                },
                "monitoring": {
                    "original": [[0]],
                    "converted": [[]]
                }
            }}
        )

        algorithm.prototypes = [simple_prototype(), simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"data": {
                "prototypes": {
                    "original": [[5, 5]],  # FIXME: hier bin ich mir nicht sicher, ob dass das sagt, was ich gern hätte...
                    "converted": [[3, 3]]
                },
                "monitoring": {
                    "original": [[4]],
                    "converted": [[3]]
                }
            }}
        )

        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(
            decorator.descriptive_data(),
            {"data": {
                "prototypes": {
                    "original": [[5, 5]],  # FIXME: please check!
                    "converted": [[3, 3]]
                },
                "monitoring": {
                    "original": [[4], [4]],
                    "converted": [[3], [3]]
                }
            }}
        )

    def test_update(self):
        decorator = DataDecorator()
        decorator._data = {
            "prototypes": {
                "original": [[10, 20, 100]],  # FIXME: please check!
                "converted": [[5, 10, 10]]
            },
            "monitoring": {
                "original": [[80]],
                "converted": [[10]]
            }
        }
        second_decorator = DataDecorator()
        second_decorator._data = {
            "prototypes": {
                "original": [[10, 20, 100]],  # FIXME: please check!
                "converted": [[5, 10, 10]]
            },
            "monitoring": {
                "original": [[100]],
                "converted": [[20]]
            }
        }
        decorator.update(second_decorator)
        self.assertEqual(decorator.data(), {
            "prototypes": {
                "original": [[10, 20, 100]],  # FIXME: please check!
                "converted": [[5, 10, 10]]
            },
            "monitoring": {
                "original": [[80], [100]],
                "converted": [[10], [20]]
            }
        })
