import unittest

from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import TrafficEvent
from assess.prototypes.simpleprototypes import Prototype
from assess.exceptions.exceptions import EventNotSupportedException

from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestTreeDistanceAlgorithm(unittest.TestCase):
    def test_representation(self):
        algorithm = TreeDistanceAlgorithm()
        self.assertEqual(algorithm.__repr__(), "TreeDistanceAlgorithm (cache_statistics=None, supported=['ProcessStartEvent'])")

    def test_update_distance(self):
        algorithm = TreeDistanceAlgorithm()
        self.assertRaises(NotImplementedError, algorithm._update_distances, None, None)

    def test_traffic(self):
        algorithm = TreeDistanceAlgorithm()
        self.assertRaises(
            EventNotSupportedException,
            algorithm.add_event,
            TrafficEvent(tme=0, pid=2, ppid=1, value=0.5)
        )

    def test_event_counts(self):
        algorithm = TreeDistanceAlgorithm()
        algorithm.prototypes = [Prototype()]
        algorithm.start_tree()
        self.assertEqual(algorithm.event_counts(), [[]])
        self.assertEqual(algorithm.prototype_event_counts(), [[0]])

    def test_format_prototype_node_counts(self):
        algorithm = TreeDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        self.assertEqual(algorithm.prototype_node_counts(signature=False), [[5]])
        self.assertEqual(algorithm.prototype_node_counts(signature=True), [[3]])

    def test_format_tree_node_counts(self):
        algorithm = TreeDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        self.assertEqual(algorithm.tree_node_counts(signature=False), [])
        algorithm._tree = simple_monitoring_tree()
        self.assertEqual(algorithm.tree_node_counts(signature=False), [4])

    def test_prototype_event_counts(self):
        algorithm = TreeDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        self.assertEqual([[5]], algorithm.prototype_event_counts())
