import unittest

from assess.algorithms.treeinclusiondistancealgorithm import TreeInclusionDistanceAlgorithm
from assess.algorithms.signatures.signatures import Signature
from assess.events.events import Event
from assess.prototypes.simpleprototypes import Prototype


class TestTreeInclusionDistanceAlgorithm(unittest.TestCase):
    def setUp(self):
        self.prototype = Prototype()
        pid_count = 1
        root = self.prototype.add_node("root", tme=0, pid=pid_count, ppid=0)
        pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(i, tme=0, pid=pid_count, ppid=3)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for i in range(5):
            child_child.add_node("node", tme=0, pid=pid_count, ppid=ppid)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_position = Prototype()
        root = self.modified_prototype_position.add_node("root", tme=0, pid=pid_count, ppid=0)
        pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        child = list(root.children())[3]
        for i in range(10):
            child.add_node(i, tme=0, pid=pid_count, ppid=5)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for i in range(5):
            child_child.add_node("node", tme=0, pid=pid_count, ppid=ppid)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_position2 = Prototype()
        root = self.modified_prototype_position2.add_node("root", tme=0, pid=1, ppid=0)
        pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        child = list(root.children())[11]
        for i in range(10):
            child.add_node(i, tme=0, pid=pid_count, ppid=13)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for i in range(5):
            child_child.add_node("node", tme=0, pid=pid_count, ppid=ppid)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_name = Prototype()
        root = self.modified_prototype_name.add_node("root", tme=0, pid=1, ppid=0)
        pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child3", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(i, tme=0, pid=pid_count, ppid=3)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for i in range(5):
            child_child.add_node("node", tme=0, pid=pid_count, ppid=ppid)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_frequency = Prototype()
        root = self.modified_prototype_frequency.add_node("root", tme=0, pid=1, ppid=0)
        pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(12):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(i, tme=0, pid=pid_count, ppid=3)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for i in range(5):
            child_child.add_node("node", tme=0, pid=pid_count, ppid=ppid)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_skipped = Prototype()
        root = self.modified_prototype_skipped.add_node("root", tme=0, pid=1, ppid=0)
        pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        for i in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(i, tme=0, pid=pid_count, ppid=3)
            pid_count += 1

    def _test_algorithm(self, prototype=None, tree=None):
        algorithm = TreeInclusionDistanceAlgorithm(signature=Signature())
        algorithm.prototypes = [prototype]
        for event in Event.from_tree(tree):
            result = algorithm.add_event(event)
        return result

    def test_distance_zero(self):
        self.assertEqual(self._test_algorithm(
                prototype=self.prototype,
                tree=self.prototype
        )[0], 0)

    def test_another_position(self):
        self.assertEqual(self._test_algorithm(
                prototype=self.prototype,
                tree=self.modified_prototype_position
        )[0], 1)
