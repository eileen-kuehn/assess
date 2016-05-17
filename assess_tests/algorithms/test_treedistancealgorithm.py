import unittest

from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm


class TestTreeDistanceAlgorithm(unittest.TestCase):
    def test_representation(self):
        algorithm = TreeDistanceAlgorithm()
        self.assertEqual(algorithm.__repr__(), "TreeDistanceAlgorithm")

    def test_update_distance(self):
        algorithm = TreeDistanceAlgorithm()
        self.assertRaises(NotImplementedError, algorithm._update_distances, None, None)
