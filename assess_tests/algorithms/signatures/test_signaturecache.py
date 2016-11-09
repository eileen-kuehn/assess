import unittest
import os
import json

import assess_tests
from assess_tests.basedata import simple_additional_monitoring_tree, simple_prototype

from assess.algorithms.statistics.statistics import MeanVariance
from assess.algorithms.signatures.signatures import *


class TestSignatureCache(unittest.TestCase):
    def test_creation(self):
        cache = SignatureCache()
        self.assertIsNotNone(cache)
        self.assertEqual(cache.frequency(), 0)
        self.assertEqual(len(cache.internal()), 0)

    def test_count(self):
        cache = SignatureCache()
        self.assertEqual(cache.node_count(), 0)
        cache.add_signature(signature="test")
        self.assertEqual(cache.node_count(), 1)
        cache.add_signature(signature="test")
        self.assertEqual(cache.node_count(), 1)
        cache.add_signature(signature="hello")
        self.assertEqual(cache.node_count(), 2)
        self.assertEqual(cache.get_count(signature="test"), 2)
        self.assertEqual(cache.get_count(signature="muh"), 0)

    def test_frequency(self):
        cache = SignatureCache()
        self.assertEqual(cache.frequency(), 0)
        cache.add_signature(signature="test")
        self.assertEqual(cache.frequency(), 1)
        cache.add_signature(signature="test")
        self.assertEqual(cache.frequency(), 2)
        cache.add_signature(signature="hello")
        self.assertEqual(cache.frequency(), 3)

    def test_none(self):
        cache = SignatureCache()
        cache.add_signature(signature=None)
        cache.add_signature(signature=None)
        self.assertEqual(cache.node_count(), 1)
        self.assertEqual(cache.frequency(), 2)
        self.assertEqual(cache.get_count(signature=None), 2)


class TestPrototypeSignatureCache(unittest.TestCase):
    def test_creation(self):
        cache = PrototypeSignatureCache()
        self.assertIsNotNone(cache)
        self.assertEqual(cache.frequency(), 0)
        self.assertEqual(len(cache.internal()), 0)
        self.assertEqual(cache.get(signature="test"), dict())

    def test_count(self):
        cache = PrototypeSignatureCache()
        self.assertEqual(cache.node_count(), 0)
        cache.add_signature(signature="test", prototype="1")
        self.assertEqual(cache.node_count(), 1)
        self.assertEqual(cache.node_count(prototype="1"), 1)
        self.assertEqual(cache.node_count(prototype="2"), 0)
        cache.add_signature(signature="test", prototype="2")
        self.assertEqual(cache.node_count(prototype="1"), 1)
        self.assertEqual(cache.node_count(prototype="2"), 1)
        cache.add_signature(signature="hello", prototype="1")
        self.assertEqual(cache.node_count(), 2)
        self.assertEqual(len(cache.get(signature="test")), 2)
        self.assertEqual(cache.get(signature="test")["1"]["count"], 1)
        self.assertEqual(cache.get(signature="test")["2"]["count"], 1)
        self.assertEqual(len(cache.get(signature="muh")), 0)

    def test_frequency(self):
        cache = PrototypeSignatureCache()
        self.assertEqual(cache.frequency(), 0)
        cache.add_signature(signature="test", prototype="1", value={"duration": 1})
        cache.add_signature(signature="test", prototype="1", value={"duration": 1})
        cache.add_signature(signature="test", prototype="2", value={"duration": 2})
        self.assertEqual(cache.frequency(), 3)
        self.assertEqual(cache.frequency(prototype="1"), 2)
        self.assertEqual(cache.frequency(prototype="2"), 1)
        cache.add_signature(signature="hello", prototype="1", value={"duration": 1})
        self.assertEqual(cache.frequency(prototype="1"), 3)
        self.assertEqual(cache.frequency(prototype="2"), 1)

    def test_distance(self):
        statistic = MeanVariance()
        self.assertEqual(statistic.count, 0)
        self.assertEqual(statistic.distance(value=0), float("inf"))
        self.assertEqual(statistic.distance(value=1), float("inf"))
        self.assertEqual(statistic.distance(value=5), float("inf"))

        statistic = MeanVariance(value=5)
        self.assertEqual(statistic.count, 1)
        self.assertEqual(statistic.mean, 5)
        self.assertEqual(statistic.count, 1)
        self.assertEqual(statistic.variance, None)
        self.assertEqual(statistic.all_valid_variance, 1)
        self.assertEqual(statistic.distance(value=5), 0)
        self.assertAlmostEqual(statistic.distance(value=3), .86, 2)
        statistic.add(value=5)
        self.assertEqual(statistic.mean, 5)
        self.assertEqual(statistic.count, 2)
        self.assertEqual(statistic.variance, 0)
        self.assertEqual(statistic.distance(value=5), 0)
        self.assertAlmostEqual(statistic.distance(value=3), .86, 2)
        statistic.add(value=4)
        self.assertEqual(statistic.count, 3)
        self.assertAlmostEqual(statistic.mean, 4.667, 2)
        self.assertAlmostEqual(statistic.variance, 0.33, 2)
        self.assertAlmostEqual(statistic.distance(value=5), 0.05, 2)
        self.assertAlmostEqual(statistic.distance(value=3), 0.75, 2)

    def test_cluster_representatives(self):
        with open(self.cluster_representatives_path(), "r") as json_file:
            cluster_representative = json.load(json_file)
        signature_cache = PrototypeSignatureCache.from_cluster_representatives(
            cluster_representatives=cluster_representative["data"]
        )
        clusters = []
        for cluster in cluster_representative["data"].keys():
            clusters.append(cluster)
        for i in xrange(4):
            self.assertTrue(str(i+1) in clusters)
        self.assertIsNotNone(signature_cache)
        self.assertEqual(356, signature_cache.node_count())
        # TODO: is there more to be checked?

    def cluster_representatives_path(self):
        return os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/cluster.json"
        )

    def test_from_signatures(self):
        prototype = simple_additional_monitoring_tree()
        other_prototype = simple_prototype()
        tree_index = prototype.to_index(signature=ParentChildByNameTopologySignature())
        prototype_index = other_prototype.to_index(signature=ParentChildByNameTopologySignature())
        prototype_cache = PrototypeSignatureCache.from_signature_caches([tree_index, prototype_index], prototype=1, threshold=.9)
        self.assertEqual(9, prototype_cache.frequency())
        self.assertEqual(3, prototype_cache.node_count())
