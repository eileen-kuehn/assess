import unittest

from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import TrafficEvent
from assess.prototypes.simpleprototypes import Prototype
from assess.exceptions.exceptions import EventNotSupportedException


class TestTreeDistanceAlgorithm(unittest.TestCase):
    def test_representation(self):
        algorithm = TreeDistanceAlgorithm()
        self.assertEqual(algorithm.__repr__(), "TreeDistanceAlgorithm")

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
        self.assertEqual(algorithm.event_counts()[0], 0)
        self.assertEqual(algorithm.prototype_event_counts()[0], 0)
