import unittest

from assess.clustering.clusterdistance import ClusterDistance
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature, EnsembleSignatureCache
from assess.algorithms.signatures.signatures import *
from assess.algorithms.distances.startexitdistance import StartExitDistance

from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestClusterDistance(unittest.TestCase):
    def test_creation(self):
        distance = ClusterDistance()
        self.assertIsNotNone(distance)
        self.assertEqual(.1, distance.threshold)

    def test_mean(self):
        distance = ClusterDistance()
        prototype_one = simple_prototype()
        prototype_two = simple_monitoring_tree()
        signature = ParentChildByNameTopologySignature()
        mean_prototype = distance.mean([
            prototype_one.to_index(signature),
            prototype_two.to_index(signature)
        ])
        self.assertEqual(3, mean_prototype.node_count())

    def test_distance(self):
        distance = ClusterDistance(distance=StartExitDistance())
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature()])
        cache_one = EnsembleSignatureCache()
        cache_one = simple_prototype().to_index(signature, start_support=True, exit_support=True, cache=cache_one)
        cache_two = EnsembleSignatureCache()
        cache_two = simple_monitoring_tree().to_index(signature, start_support=True, exit_support=True, cache=cache_two)
        self.assertEqual(2, distance(cache_one, cache_two))
