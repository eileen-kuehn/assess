import unittest

from assess.algorithms.distances.startexitdistance import StartExitDistance
from assess.algorithms.signatures.signaturecache import PrototypeSignatureCache
from assess.algorithms.signatures.signatures import \
    ParentChildByNameTopologySignature, ParentChildOrderByNameTopologySignature
from assess.algorithms.statistics.setstatistics import SetStatistics
from assess.decorators.anomalydecorator import AnomalyDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.events.events import Event, TrafficEvent, ProcessStartEvent
from assess.exceptions.exceptions import EventNotSupportedException

from assess_tests.basedata import simple_monitoring_tree, simple_prototype, real_tree


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
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
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
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
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
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
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
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
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
            signature=EnsembleSignature(
                signatures=[ParentChildByNameTopologySignature(),
                            ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
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
        for event in Event.from_tree(simple_prototype(), supported={ProcessStartEvent: True}):
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
            signature=EnsembleSignature(
                signatures=[ParentChildByNameTopologySignature(),
                            ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
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
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildOrderByNameTopologySignature())
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(
            decorator.data(), [[[[False, False, False, False, True]]]])

    def test_real_trees(self):
        def distance_builder(**kwargs):
            distance = StartExitDistance()
            distance.supported[TrafficEvent] = True
            return distance
        tree_one = real_tree()
        tree_two = real_tree(path="data/c01-007-102/2/1129-2-process.csv")
        prototype_names = ["1", "2"]
        prototype_caches = []
        for index, tree in enumerate([tree_one, tree_two]):
            prototype_caches.append(PrototypeSignatureCache.from_signature_caches(
                [tree.to_index(signature=ParentChildByNameTopologySignature(),
                               start_support=True,
                               exit_support=True,
                               traffic_support=True,
                               statistics_cls=SetStatistics)],
                prototype=prototype_names[index], threshold=0))

        decorator = AnomalyDecorator()
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildByNameTopologySignature(),
            distance=distance_builder,
            cache_statistics=SetStatistics
        )
        prototype_cache = prototype_caches[0]
        for cache in prototype_caches[1:]:
            prototype_cache += cache
        algorithm.cluster_representatives(
            signature_prototypes=[prototype_cache],
            prototypes=prototype_names
        )
        decorator.wrap_algorithm(algorithm)
        for tree in [tree_one, tree_two]:
            algorithm.start_tree()
            for event in tree.event_iter(supported=algorithm.supported):
                try:
                    algorithm.add_event(event)
                except EventNotSupportedException:
                    pass
            algorithm.finish_tree()
        # First tree vs. first is False for start
        self.assertFalse(decorator.data()[0][0][0][0])
        # ... and end
        self.assertFalse(decorator.data()[0][0][0][-1])
        # First tree vs. second is False for start
        self.assertFalse(decorator.data()[0][0][1][0])
        # and True for end
        self.assertTrue(decorator.data()[0][0][1][-1])
        # Second tree vs. first is False for start
        self.assertFalse(decorator.data()[1][0][0][0])
        # ... and True for end
        self.assertTrue(decorator.data()[1][0][0][-1])
        # Second tree vs. second is False for start
        self.assertFalse(decorator.data()[1][0][1][0])
        # ... and False for end
        self.assertFalse(decorator.data()[1][0][1][-1])
