import unittest

from assess.decorators.distancedecorator import DistanceDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import Event
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.algorithms.signatures.signatures import *

from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestDistanceDecorator(unittest.TestCase):
    def test_creation(self):
        decorator = DistanceDecorator(normalized=False)
        self.assertEqual(decorator._name, "distances")
        self.assertEqual([], decorator.data())
        self.assertEqual({"distances": []}, decorator.descriptive_data())

        decorator = DistanceDecorator(normalized=True)
        self.assertEqual(decorator._name, "normalized_distances")
        self.assertEqual([], decorator.data())
        self.assertEqual({"normalized_distances": []}, decorator.descriptive_data())

    def test_simple(self):
        decorator = DistanceDecorator(normalized=False)
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]

        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        self.assertEqual({'distances': [[[[]]]]}, decorator.descriptive_data())
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[[[2, 1, 1, 0]]]], decorator.data())

    def test_two_prototypes(self):
        decorator = DistanceDecorator(normalized=False)
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        self.assertEqual([[[[], []]]], decorator.data())
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[[[2, 1, 1, 0], [2, 1, 1, 0]]]], decorator.data())

    def test_ensemble(self):
        decorator = DistanceDecorator(normalized=False)
        algorithm = IncrementalDistanceAlgorithm(
           signature=EnsembleSignature(signatures=[ParentChildByNameTopologySignature(),
                                                   ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype()]

        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        self.assertEqual([[[[]], [[]]]], decorator.data())
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[[[2, 1, 1, 0]], [[4, 3, 3, 2]]]], decorator.data())

    def test_two_prototypes_and_ensemble(self):
        decorator = DistanceDecorator(normalized=False)
        algorithm = IncrementalDistanceAlgorithm(
           signature=EnsembleSignature(signatures=[ParentChildByNameTopologySignature(),
                                                   ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        self.assertEqual([[[[], []], [[], []]]], decorator.data())
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[[[2, 1, 1, 0], [2, 1, 1, 0]], [[4, 3, 3, 2], [2, 1, 1, 0]]]], decorator.data())

    def test_normalized_results(self):
        decorator = DistanceDecorator(normalized=True)
        algorithm = IncrementalDistanceAlgorithm(
            signature=EnsembleSignature(signatures=[ParentChildByNameTopologySignature(),
                                                    ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        self.assertEqual([[[[], []], [[], []]]], decorator.data())
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()

        self.assertEqual([[[[.5, .2, .2, 0.0], [.5, .2, .2, 0.0]],
                           [[.6666666666666666, .42857142857142855, .42857142857142855, .25], [.5, .2, .2, 0.0]]]], decorator.data())
