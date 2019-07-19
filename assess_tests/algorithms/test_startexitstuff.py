import unittest

from assess.prototypes.simpleprototypes import Prototype
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.algorithms.distances.startexitdistance import StartExitDistance
from assess.events.events import Event


class TestStartExitStuff(unittest.TestCase):
    def setUp(self):
        self._simple_prototype = Prototype()
        root = self._simple_prototype.add_node(
            "root_node", tme=0, exit_tme=10, pid=2, ppid=1)
        root.add_node("first_child", tme=1, exit_tme=3, pid=3, ppid=2)
        root.add_node("second_child", tme=1, exit_tme=4, pid=4, ppid=2)
        root.add_node("first_child", tme=5, exit_tme=7, pid=5, ppid=2)

    def test_start_exit(self):
        signature = ParentChildByNameTopologySignature()
        alg = IncrementalDistanceAlgorithm(
            signature=signature, distance=StartExitDistance)
        alg.prototypes = [self._simple_prototype]

        alg.start_tree()
        alg.add_event(Event.start(tme=0, pid=2, ppid=1, name="root_node"))
        alg.add_event(Event.start(tme=1, pid=3, ppid=2, name="first_child"))
        alg.add_event(Event.start(tme=1, pid=4, ppid=2, name="second_child"))
        alg.add_event(Event.exit(
            tme=3, start_tme=1, pid=3, ppid=2, name="first_child"))
        alg.add_event(Event.exit(
            tme=4, start_tme=1, pid=4, ppid=2, name="second_child"))
        alg.add_event(Event.start(tme=5, pid=5, ppid=2, name="first_child"))
        alg.add_event(Event.exit(
            tme=7, start_tme=5, pid=5, ppid=2, name="first_child"))
        distance = alg.add_event(Event.exit(
            tme=10, start_tme=0, pid=2, ppid=1, name="root_node"))
        alg.finish_tree()
        self.assertEqual(distance[0][0], [0])
