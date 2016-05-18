import unittest

from assess.algorithms.distances.distance import Distance


class TestDistance(unittest.TestCase):
    def test_creation(self):
        distance = Distance(prototypes=["1", "2", "3"])
        for index, dist in enumerate(distance):
            self.assertEqual(dist, 0)
        self.assertEqual(index, 2)
        self.assertEqual(distance.node_count(), 0)
        self.assertFalse(distance.is_prototype_based_on_original())

    def test_raises(self):
        distance = Distance()
        self.assertRaises(NotImplementedError, distance.update_distance)
        self.assertRaises(NotImplementedError, distance.finish_distance)

    def test_adding_of_results(self):
        distance = Distance()
        self.assertEqual(
            distance._add_result_dicts({"1": 0, "2": 0}, {"1": 1, "2": 1}),
            {"1": 1, "2": 1}
        )
        self.assertEqual(
            distance._add_result_dicts({"1": 1, "2": 1}, {"1": 2, "2": -1}),
            {"1": 3, "2": 0}
        )
        self.assertEqual(
            distance._add_result_dicts({"1": 1}, {"2": 1}),
            {"1": 1, "2": 1}
        )
        self.assertEqual(
            distance._add_result_dicts({"1": 2, "2": 0}, {"1": -1, "3": -.5}),
            {"1": 1, "2": 0, "3": -.5}
        )
