import unittest
import os
import json

import assess_tests
from assess.algorithms.statistics.setstatistics import SetStatistics
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess_tests.basedata import simple_additional_monitoring_tree, simple_prototype, real_tree

from assess.algorithms.statistics.statistics import MeanVariance
from assess.algorithms.signatures.signatures import *


class TestSignatureCache(unittest.TestCase):
    def test_creation(self):
        cache = SignatureCache()
        self.assertIsNotNone(cache)
        self.assertEqual(cache.multiplicity(), 0)
        self.assertEqual(len(cache.internal()), 0)

    def test_count(self):
        cache = SignatureCache(supported={object: True})
        self.assertEqual(cache.node_count(), 0)
        cache["test", object] = {"count": 0}
        self.assertEqual(cache.node_count(), 1)
        cache["test", object] = {"count": 0}
        self.assertEqual(cache.node_count(), 1)
        cache["hello", object] = {"count": 0}
        self.assertEqual(cache.node_count(), 2)
        self.assertEqual(cache.multiplicity(signature="test"), 2)
        self.assertEqual(cache.multiplicity(signature="muh"), 0)

    def test_frequency(self):
        cache = SignatureCache(supported={object: True})
        self.assertEqual(cache.multiplicity(), 0)
        cache["test", object] = {"count": 0}
        self.assertEqual(cache.multiplicity(), 1)
        cache["test", object] = {"count": 0}
        self.assertEqual(cache.multiplicity(), 2)
        cache["hello", object] = {"count": 0}
        self.assertEqual(cache.multiplicity(), 3)

    def test_none(self):
        cache = SignatureCache(supported={object: True})
        cache[None, object] = {"count": 0}
        cache[None, object] = {"count": 0}
        self.assertEqual(cache.node_count(), 1)
        self.assertEqual(cache.multiplicity(), 2)
        self.assertEqual(cache.multiplicity(signature=None), 2)


class TestPrototypeSignatureCache(unittest.TestCase):
    def test_creation(self):
        cache = PrototypeSignatureCache()
        self.assertIsNotNone(cache)
        self.assertEqual(cache.multiplicity(), 0)
        self.assertEqual(len(cache.internal()), 0)
        self.assertEqual(cache.get(signature="test"), dict())

    def test_count(self):
        cache = PrototypeSignatureCache(supported={object: True})
        self.assertEqual(cache.node_count(), 0)
        cache["test", "1", object] = {"count": 0}
        self.assertEqual(cache.node_count(), 1)
        self.assertEqual(cache.node_count(prototype="1"), 1)
        self.assertEqual(cache.node_count(prototype="2"), 0)
        cache["test", "2", object] = {"count": 0}
        self.assertEqual(cache.node_count(prototype="1"), 1)
        self.assertEqual(cache.node_count(prototype="2"), 1)
        cache["hello", "1", object] = {"count": 0}
        self.assertEqual(cache.node_count(), 2)
        self.assertEqual(len(cache.get(signature="test")), 2)
        self.assertEqual(cache.get(signature="test")["1"][object]["count"].count(), 1)
        self.assertEqual(cache.get(signature="test")["2"][object]["count"].count(), 1)
        self.assertEqual(len(cache.get(signature="muh")), 0)

    def test_frequency(self):
        cache = PrototypeSignatureCache(supported={object: True})
        self.assertEqual(cache.multiplicity(), 0)
        cache["test", "1", object] = {"count": 0, "duration": 1}
        cache["test", "1", object] = {"count": 0, "duration": 1}
        cache["test", "2", object] = {"count": 0, "duration": 2}
        self.assertEqual(cache.multiplicity(), 3)
        self.assertEqual(cache.multiplicity(prototype="1"), 2)
        self.assertEqual(cache.multiplicity(prototype="2"), 1)
        cache["hello", "1", object] = {"count": 0, "duration": 1}
        self.assertEqual(cache.multiplicity(prototype="1"), 3)
        self.assertEqual(cache.multiplicity(prototype="2"), 1)

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
        self.assertEqual(statistic.variance, 0)
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
        cache = SignatureCache(supported={ProcessStartEvent: True, ProcessExitEvent: True,
                                          TrafficEvent: True}, statistics_cls=SetStatistics)
        cache_two = SignatureCache(supported={ProcessStartEvent: True, ProcessExitEvent: True,
                                          TrafficEvent: True}, statistics_cls=SetStatistics)
        prototype = simple_additional_monitoring_tree()
        other_prototype = simple_prototype()
        tree_index = prototype.to_index(signature=ParentChildByNameTopologySignature(), cache=cache)
        prototype_index = other_prototype.to_index(signature=ParentChildByNameTopologySignature(), cache=cache_two)
        prototype_cache = PrototypeSignatureCache.from_signature_caches([tree_index, prototype_index], prototype=1, threshold=.9)
        self.assertEqual(9, prototype_cache.multiplicity())
        self.assertEqual(3, prototype_cache.node_count())

    def test_from_signature_frequency(self):
        def cache_builder():
            return SignatureCache(supported={ProcessStartEvent: True, ProcessExitEvent: True,
                                             TrafficEvent: True}, statistics_cls=SetStatistics)
        prototype = simple_prototype()
        signature = ParentChildByNameTopologySignature()
        validation_index = prototype.to_index(signature=signature, cache=cache_builder())
        prototype_index = PrototypeSignatureCache.from_signature_caches(
            [prototype.to_index(signature, cache=cache_builder()) for _ in range(10)],
            prototype=prototype,
            threshold=0)
        self.assertEqual(validation_index.multiplicity(), prototype_index.multiplicity())
        for token in validation_index:
            self.assertEqual(validation_index.multiplicity(signature=token),
                             prototype_index.multiplicity(signature=token, prototype=prototype))

    def test_merging(self):
        signature = ParentChildByNameTopologySignature()
        one = simple_prototype()
        two = simple_additional_monitoring_tree()
        prototype_one = one.to_prototype(signature=signature, start_support=True, exit_support=False,
                                         traffic_support=False, statistics_cls=SetStatistics)
        prototype_two = two.to_prototype(signature=signature, start_support=True, exit_support=False,
                                         traffic_support=False, statistics_cls=SetStatistics)
        self.assertEqual(one.node_count(), prototype_one.multiplicity(prototype=one))
        self.assertEqual(two.node_count(), prototype_two.multiplicity(prototype=two))
        self.assertEqual(0, prototype_one.multiplicity(two))
        prototype_one += prototype_two
        self.assertEqual(one.node_count(), prototype_one.multiplicity(prototype=one))
        self.assertEqual(two.node_count(), prototype_one.multiplicity(prototype=two))
        self.assertEqual(one.node_count() + two.node_count(), prototype_one.multiplicity())

        prototype_three = one.to_prototype(signature=signature, start_support=True, exit_support=True,
                                         traffic_support=False, statistics_cls=SetStatistics)
        prototype_four = two.to_prototype(signature=signature, start_support=True, exit_support=True,
                                         traffic_support=False, statistics_cls=SetStatistics)
        self.assertEqual(one.node_count()*2, prototype_three.multiplicity(prototype=one))
        self.assertEqual(two.node_count()*2, prototype_four.multiplicity(prototype=two))
        self.assertEqual(0, prototype_three.multiplicity(two))
        prototype_three += prototype_four
        self.assertEqual(one.node_count()*2, prototype_three.multiplicity(prototype=one))
        self.assertEqual(two.node_count()*2, prototype_three.multiplicity(prototype=two))
        self.assertEqual(one.node_count()*2 + two.node_count()*2, prototype_three.multiplicity())

    def test_cluster_representatives(self):
        tree_1 = real_tree()
        tree_2 = real_tree()
        signature = ParentChildByNameTopologySignature()
        signature_caches = []
        for tree in [tree_1, tree_2]:
            signature_caches.append(tree.to_index(
                signature=signature, start_support=True, exit_support=True, traffic_support=True,
                statistics_cls=SetStatistics))

        cr = PrototypeSignatureCache.from_signature_caches(signature_caches, prototype=tree_1)
        for token in cr:
            self.assertEqual(cr.multiplicity(token, tree_1), signature_caches[0].multiplicity(token))
            self.assertEqual(cr.get_statistics(signature=token, key="duration", prototype=tree_1, event_type=ProcessExitEvent).count(),
                             signature_caches[0].get_statistics(signature=token, key="duration", event_type=ProcessExitEvent).count())
