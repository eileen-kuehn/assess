import unittest

from assess.prototypes.simpleprototypes import Prototype
from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.treeeditdistancealgorithm import TreeEditDistanceAlgorithm
from assess.events.events import Event


class TestTreeEditDistanceFunctionalities(unittest.TestCase):
    def setUp(self):
        self.prototype = Prototype()
        root = self.prototype.add_node("root", tme=0, exit_tme=0, pid=1, ppid=0)
        root.add_node("test", tme=0, exit_tme=0, pid=2, ppid=1)
        root.add_node("muh", tme=0, exit_tme=0, pid=3, ppid=1)
        list(root.children())[0].add_node("yes", tme=0, exit_tme=0, pid=4, ppid=2)

        self.modified_position = Prototype()
        root = self.modified_position.add_node("root", pid=1, ppid=0, tme=0, exit_tme=0)
        root.add_node("test", tme=0, pid=2, ppid=1, exit_tme=0)
        root.add_node("muh", tme=0, pid=3, ppid=1, exit_tme=0)
        list(root.children())[1].add_node("yes", tme=0, pid=4, ppid=3, exit_tme=0)

        self.modified_name = Prototype()
        root = self.modified_name.add_node("root", pid=1, ppid=0, tme=0, exit_tme=0)
        root.add_node("test", tme=0, pid=2, ppid=1, exit_tme=0)
        root.add_node("muh", tme=0, pid=3, ppid=1, exit_tme=0)
        list(root.children())[0].add_node("no", tme=0, pid=4, ppid=2, exit_tme=0)

    def _test_algorithm(self, prototype=None, tree=None):
        signature = Signature()
        algorithm = TreeEditDistanceAlgorithm(signature=signature)
        algorithm.prototypes = [prototype]

        algorithm.start_tree()
        result = algorithm.add_events(Event.from_tree(tree))
        algorithm.finish_tree()
        return result

    def test_zero_distance(self):
        self.assertEqual(self._test_algorithm(
            prototype=self.prototype,
            tree=self.prototype
        )[0], 0)

    def test_modified_position(self):
        self.assertEqual(self._test_algorithm(
            prototype=self.prototype,
            tree=self.modified_position
        )[0], 2)

    def test_modified_name(self):
        self.assertEqual(self._test_algorithm(
            prototype=self.prototype,
            tree=self.modified_name
        )[0], 1)
