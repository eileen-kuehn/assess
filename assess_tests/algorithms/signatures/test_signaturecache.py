import unittest

from assess.algorithms.signatures.signaturecache import SignatureCache, PrototypeSignatureCache,\
    MeanVariance


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
        self.assertEqual(cache.get(signature="test"), 2)
        self.assertEqual(cache.get(signature="muh"), 0)

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
        self.assertEqual(cache.get(signature=None), 2)


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
        self.assertEqual(cache.get(signature="test")["1"].count, 1)
        self.assertEqual(cache.get(signature="test")["2"].count, 1)
        self.assertEqual(len(cache.get(signature="muh")), 0)

    def test_frequency(self):
        cache = PrototypeSignatureCache()
        self.assertEqual(cache.frequency(), 0)
        cache.add_signature(signature="test", prototype="1", value=1)
        cache.add_signature(signature="test", prototype="1", value=1)
        cache.add_signature(signature="test", prototype="2", value=2)
        self.assertEqual(cache.frequency(), 3)
        self.assertEqual(cache.frequency(prototype="1"), 2)
        self.assertEqual(cache.frequency(prototype="2"), 1)
        cache.add_signature(signature="hello", prototype="1", value=1)
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
        self.assertEqual(statistic._mean, 5)
        self.assertEqual(statistic._count, 1)
        self.assertEqual(statistic._variance, 0)
        self.assertEqual(statistic.distance(value=5), 0)
        self.assertAlmostEqual(statistic.distance(value=3), .86, 2)
        statistic.add(value=5)
        self.assertEqual(statistic._mean, 5)
        self.assertEqual(statistic._count, 2)
        self.assertEqual(statistic._variance, 0)
        self.assertEqual(statistic.distance(value=5), 0)
        self.assertAlmostEqual(statistic.distance(value=3), .76, 2)  # improvement because of count
        statistic.add(value=4)
        self.assertEqual(statistic._count, 3)
        self.assertAlmostEqual(statistic._mean, 4.667, 2)
        self.assertAlmostEqual(statistic._variance, 0.667, 2)
        self.assertAlmostEqual(statistic.distance(value=5), 0.08, 2)
        self.assertAlmostEqual(statistic.distance(value=3), 0.88, 2)
