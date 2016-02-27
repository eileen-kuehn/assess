import unittest

from assess.prototypes.simpleprototypes import Prototype
from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.treeeditdistancealgorithm import TreeEditDistanceAlgorithm
from assess.events.events import Event


class TestTreeEditDistanceFunctionalities(unittest.TestCase):
    def setUp(self):
        self.prototype = Prototype()
        root = self.prototype.add_node("root", tme=0, pid=1, ppid=0)
        root.add_child("test", tme=0)
        root.add_child("muh", tme=0)
        list(root.children())[0].add_child("yes", tme=0)

        self.modified_position = Prototype()
        root = self.modified_position.add_node("root", pid=1, ppid=0, tme=0)
        root.add_child("test", tme=0)
        root.add_child("muh", tme=0)
        list(root.children())[1].add_child("yes", tme=0)

        self.modified_name = Prototype()
        root = self.modified_name.add_node("root", pid=1, ppid=0, tme=0)
        root.add_child("test", tme=0)
        root.add_child("muh", tme=0)
        list(root.children())[0].add_child("no", tme=0)

    def _test_algorithm(self, prototype=None, tree=None):
        signature = Signature()
        algorithm = TreeEditDistanceAlgorithm(signature=signature)
        algorithm.prototypes = [prototype]

        result = algorithm.add_events(Event.from_tree(tree))
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
