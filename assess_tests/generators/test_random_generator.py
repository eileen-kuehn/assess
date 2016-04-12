import unittest

from assess.generators.random_generator import RandomGenerator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.decorators.distancedecorator import DistanceDecorator
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature


class TestRandomGenerator(unittest.TestCase):
    def setUp(self):
        pass

    def test_default_generator(self):
        rg = RandomGenerator()
        self.assertIsNotNone(rg, "the random generator has not been created")

        prototype = rg.prototype
        self.assertIsNotNone(prototype, "the prototype created should not be None")

        event_counter = 0
        for event in rg:
            self.assertIsNotNone(event)
            event_counter += 1
        self.assertEqual(event_counter, 101*2)

    def test_default_generator_incremental_distance(self):
        rg = RandomGenerator(seed=1234)
        alg = IncrementalDistanceAlgorithm()
        alg.prototypes = [rg.prototype]

        vector_decorator = DistanceDecorator()
        vector_decorator._algorithm = alg

        vector_decorator.start_tree()
        for event in rg:
            distance = vector_decorator.add_event(event)
        vector_decorator.finish_tree()
        print(vector_decorator.data())
        self.assertEqual(distance[0], 107)

    def test_maximum_generator_incremental_distance(self):
        rg = RandomGenerator(relative_matching=1)
        alg = IncrementalDistanceAlgorithm()
        alg.prototypes = [rg.prototype]

        decorator = DistanceDecorator(normalized=True)
        decorator.algorithm = alg

        decorator.start_tree()
        for event in rg:
            distance = decorator.add_event(event)
        decorator.finish_tree()
        print(decorator.data())
        self.assertEqual(distance[0], 0)

    def test_maximum_generator_newerincremental_with_signature_distance(self):
        rg = RandomGenerator(relative_matching=1)
        signature = ParentChildByNameTopologySignature()
        alg = IncrementalDistanceAlgorithm(signature=signature)
        alg.prototypes = [rg.prototype]

        decorator = DistanceDecorator(normalized=True)
        decorator.algorithm = alg

        decorator.start_tree()
        for event in rg:
            distance = decorator.add_event(event)
        decorator.finish_tree()
        self.assertEqual(decorator.data()[-1][-1][-1], 0)