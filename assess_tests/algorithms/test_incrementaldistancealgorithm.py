import unittest

from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import *
from assess.prototypes.simpleprototypes import Prototype
from assess.events.events import Event


class TestIncrementalDistanceAlgorithmFunctionality(unittest.TestCase):
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

    def _add_events(self, algorithm=None, events=None):
        algorithm.start_tree()
        for event in Event.from_tree(events):
            result = algorithm.add_event(event)
        algorithm.finish_tree()
        return result

    def _test_signature(self, algorithm=None, signature=None, events=None, prototype=None):
        if prototype is None:
            prototype = self.prototype
        signature = signature()
        algorithm = algorithm(signature=signature)
        algorithm.prototypes = [prototype]

        return self._add_events(algorithm=algorithm, events=events)

    def _test_symmetry(self, algorithm=None, signature=None, prototype=None, tree=None):
        if prototype is None:
            prototype = self.prototype
        self.assertEqual(
                self._test_signature(
                        algorithm=algorithm,
                        signature=signature,
                        prototype=prototype,
                        events=tree
                ), self._test_signature(
                        algorithm=algorithm,
                        signature=signature,
                        prototype=tree,
                        events=prototype
                )
        )

    def _test_prototype_count(self, algorithm=None, signature=None):
        signature = signature()
        algorithm = algorithm(signature=signature)
        algorithm.prototypes = [self.prototype]
        return algorithm.prototype_counts()

    def test_distance_zero(self):
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.prototype
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.prototype
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.prototype
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.prototype
        )[0], 0)

    def test_another_child(self):
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_position
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_position
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_position
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_position
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_position
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_position
        )[0], 26)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_position
        )[0], 28)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_position
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_position
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=10),
                events=self.modified_prototype_position
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=100),
                events=self.modified_prototype_position
        )[0], 30)

    def test_another_child2(self):
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_position2
        )[0], 22)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_position2
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_position2
        )[0], 22)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_position2
        )[0], 22)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_position2
        )[0], 24)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_position2
        )[0], 26)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_position2
        )[0], 28)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_position2
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_position2
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=10),
                events=self.modified_prototype_position2
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=100),
                events=self.modified_prototype_position2
        )[0], 30)

    def test_another_name(self):
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_name
        )[0], 1)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_name
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_name
        )[0], 2)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_name
        )[0], 1)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_name
        )[0], 4)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_name
        )[0], 7) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_name
        )[0], 10) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_name
        )[0], 13) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_name
        )[0], 16) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=6),
                events=self.modified_prototype_name
        )[0], 19) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=7),
                events=self.modified_prototype_name
        )[0], 22) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
                events=self.modified_prototype_name
        )[0], 25) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=9),
                events=self.modified_prototype_name
        )[0], 28) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=10),
                events=self.modified_prototype_name
        )[0], 30) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=11),
                events=self.modified_prototype_name
        )[0], 31) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=12),
                events=self.modified_prototype_name
        )[0], 32) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=13),
                events=self.modified_prototype_name
        )[0], 33) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=14),
                events=self.modified_prototype_name
        )[0], 34) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=15),
                events=self.modified_prototype_name
        )[0], 35) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
                events=self.modified_prototype_name
        )[0], 36) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=17),
                events=self.modified_prototype_name
        )[0], 37) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=18),
                events=self.modified_prototype_name
        )[0], 38) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=19),
                events=self.modified_prototype_name
        )[0], 39) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=20),
                events=self.modified_prototype_name
        )[0], 40) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=100),
                events=self.modified_prototype_name
        )[0], 40) # TODO: check

    def test_another_frequency(self):
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_frequency
        )[0], 2)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=6),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=7),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=9),
                events=self.modified_prototype_frequency
        )[0], 0)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=10),
                events=self.modified_prototype_frequency
        )[0], 1)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=11),
                events=self.modified_prototype_frequency
        )[0], 4) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=12),
                events=self.modified_prototype_frequency
        )[0], 6) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=13),
                events=self.modified_prototype_frequency
        )[0], 8) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=14),
                events=self.modified_prototype_frequency
        )[0], 10) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=15),
                events=self.modified_prototype_frequency
        )[0], 12) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
                events=self.modified_prototype_frequency
        )[0], 14) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=18),
                events=self.modified_prototype_frequency
        )[0], 18) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=19),
                events=self.modified_prototype_frequency
        )[0], 20) # TODO: check
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=20),
                events=self.modified_prototype_frequency
        )[0], 22)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=21),
                events=self.modified_prototype_frequency
        )[0], 24)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=22),
                events=self.modified_prototype_frequency
        )[0], 26)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=23),
                events=self.modified_prototype_frequency
        )[0], 28)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=24),
                events=self.modified_prototype_frequency
        )[0], 30)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=25),
                events=self.modified_prototype_frequency
        )[0], 32)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=26),
                events=self.modified_prototype_frequency
        )[0], 34)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=27),
                events=self.modified_prototype_frequency
        )[0], 36)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=28),
                events=self.modified_prototype_frequency
        )[0], 38)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=29),
                events=self.modified_prototype_frequency
        )[0], 40)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=30),
                events=self.modified_prototype_frequency
        )[0], 42)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=31),
                events=self.modified_prototype_frequency
        )[0], 42)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=100),
                events=self.modified_prototype_frequency
        )[0], 42)

    def test_another_skipped(self):
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_skipped
        )[0], 1)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_skipped
        )[0], 5)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_skipped
        )[0], 1)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_skipped
        )[0], 1)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_skipped
        )[0], 2)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_skipped
        )[0], 3)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_skipped
        )[0], 4)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_skipped
        )[0], 5)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_skipped
        )[0], 5)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=10),
                events=self.modified_prototype_skipped
        )[0], 5)
        self.assertEqual(self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=100),
                events=self.modified_prototype_skipped
        )[0], 5)

    def test_symmetry_zero(self):
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildByNameTopologySignature(),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature(),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature(),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
            tree=self.prototype
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
            tree=self.prototype
        )

    def test_symmetry_child(self):
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildByNameTopologySignature(),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature(),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature(),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
            tree=self.modified_prototype_position
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
            tree=self.modified_prototype_position
        )

    def test_symmetry_child2(self):
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildByNameTopologySignature(),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature(),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature(),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
            tree=self.modified_prototype_position2
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
            tree=self.modified_prototype_position2
        )

    def test_symmetry_name(self):
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildByNameTopologySignature(),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature(),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature(),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
            tree=self.modified_prototype_name
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
            tree=self.modified_prototype_name
        )

    def test_symmetry_frequency(self):
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildByNameTopologySignature(),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature(),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature(),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
            tree=self.modified_prototype_frequency
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
            tree=self.modified_prototype_frequency
        )

    def test_symmetry_skipped(self):
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildByNameTopologySignature(),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature(),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature(),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
            tree=self.modified_prototype_skipped
        )
        self._test_symmetry(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16),
            tree=self.modified_prototype_skipped
        )

    def test_node_count(self):
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildByNameTopologySignature()
        )[0], 14)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature()
        )[0], 56)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature()
        )[0], 16)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0)
        )[0], 14)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1)
        )[0], 18)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2)
        )[0], 22)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3)
        )[0], 26)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4)
        )[0], 30)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5)
        )[0], 33)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=6)
        )[0], 36)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=7)
        )[0], 39)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8)
        )[0], 42)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=9)
        )[0], 45)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=10)
        )[0], 46)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=11)
        )[0], 47)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=12)
        )[0], 48)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=13)
        )[0], 49)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=14)
        )[0], 50)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=15)
        )[0], 51)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16)
        )[0], 52)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=17)
        )[0], 53)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=18)
        )[0], 54)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=19)
        )[0], 55)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=20)
        )[0], 56)
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=100)
        )[0], 56)
