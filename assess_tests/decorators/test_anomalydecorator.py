import unittest

from assess.decorators.anomalydecorator import AnomalyDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import *
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.events.events import Event

from assess_tests.basedata import simple_monitoring_tree, simple_prototype, simple_unique_node_tree


class TestAnomalyDecorator(unittest.TestCase):
    def test_creation(self):
        decorator = AnomalyDecorator()
        self.assertEqual(decorator.data(), [])
        self.assertEqual(decorator.descriptive_data(), {"anomaly": []})

    def test_simple(self):
        decorator = AnomalyDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [
            [
                [
                    [False, False, False, False, False]
                ]
            ]
        ])

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [
            [
                [
                    [False, False, False, False, False]
                ]
            ],
            [
                [
                    [False, False, False, False, False]
                ]
            ]
        ])

    def test_two_prototypes(self):
        decorator = AnomalyDecorator()
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [
            [
                [
                    [False, False, False, False, False],
                    [False, False, False, False, False]
                ]
            ]
        ])

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [
            [
                [
                    [False, False, False, False, False],
                    [False, False, False, False, False]
                ]
            ],
            [
                [
                    [False, False, False, False, False],
                    [False, False, False, False, False]
                ]
            ]
        ])

    def test_two_ensembles(self):
        decorator = AnomalyDecorator()
        algorithm = IncrementalDistanceAlgorithm(
            signature=EnsembleSignature(signatures=[ParentChildByNameTopologySignature(),
                                                    ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [
            [
                [
                    [False, False, False, False, False]
                ],
                [
                    [False, False, False, False, True]
                ]
            ]
        ])

        algorithm.start_tree()
        for event in Event.from_tree(simple_prototype()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [
            [
                [
                    [False, False, False, False, False]
                ],
                [
                    [False, False, False, False, True]
                ]
            ],
            [
                [
                    [False, False, False, False, False, False]
                ],
                [
                    [False, False, False, False, False, False]
                ]
            ]
        ])

    def test_ensemble_with_prototypes(self):
        decorator = AnomalyDecorator()
        algorithm = IncrementalDistanceAlgorithm(
            signature=EnsembleSignature(signatures=[ParentChildByNameTopologySignature(), ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [
            [
                [
                    [False, False, False, False, False],
                    [False, False, False, False, False]
                ],
                [
                    [False, False, False, False, True],
                    [False, False, False, False, False]
                ]
            ]
        ])

    def test_single(self):
        decorator = AnomalyDecorator()
        algorithm = IncrementalDistanceAlgorithm(signature=ParentChildOrderByNameTopologySignature())
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.data(), [[[[False, False, False, False, True]]]])
