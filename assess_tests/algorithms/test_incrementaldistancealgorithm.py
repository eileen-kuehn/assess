import unittest

from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.algorithms.distances.simpledistance import SimpleDistance
from assess.algorithms.signatures.signatures import ParentChildOrderTopologySignature, \
    ParentChildOrderByNameTopologySignature, \
    ParentCountedChildrenByNameTopologySignature, ParentChildByNameTopologySignature
from assess.prototypes.simpleprototypes import Prototype
from assess.events.events import Event, TrafficEvent, ProcessStartEvent
from assess.exceptions.exceptions import EventNotSupportedException,\
    TreeNotStartedException

from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestIncrementalDistanceAlgorithmFunctionality(unittest.TestCase):
    def setUp(self):
        self.prototype = Prototype()
        pid_count = 1
        root = self.prototype.add_node(
            "root", tme=0, pid=pid_count, ppid=0, exit_tme=0)
        pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(str(i), tme=0, pid=pid_count, ppid=3, exit_tme=0)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for _ in range(5):
            child_child.add_node(
                "node", tme=0, pid=pid_count, ppid=ppid, exit_tme=0)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_position = Prototype()
        root = self.modified_prototype_position.add_node(
            "root", tme=0, pid=pid_count, ppid=0, exit_tme=0)
        pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        child = list(root.children())[3]
        for i in range(10):
            child.add_node(str(i), tme=0, pid=pid_count, ppid=5, exit_tme=0)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for _ in range(5):
            child_child.add_node(
                "node", tme=0, pid=pid_count, ppid=ppid, exit_tme=0)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_position2 = Prototype()
        root = self.modified_prototype_position2.add_node(
            "root", tme=0, pid=1, ppid=0, exit_tme=0)
        pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        child = list(root.children())[11]
        for i in range(10):
            child.add_node(str(i), tme=0, pid=pid_count, ppid=13, exit_tme=0)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for _ in range(5):
            child_child.add_node(
                "node", tme=0, pid=pid_count, ppid=ppid, exit_tme=0)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_name = Prototype()
        root = self.modified_prototype_name.add_node(
            "root", tme=0, pid=1, ppid=0, exit_tme=0)
        pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child3", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(str(i), tme=0, pid=pid_count, ppid=3, exit_tme=0)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for _ in range(5):
            child_child.add_node(
                "node", tme=0, pid=pid_count, ppid=ppid, exit_tme=0)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_frequency = Prototype()
        root = self.modified_prototype_frequency.add_node(
            "root", tme=0, pid=1, ppid=0, exit_tme=0)
        pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(12):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(str(i), tme=0, pid=pid_count, ppid=3, exit_tme=0)
            pid_count += 1
        child_child = list(child.children())[5]
        ppid = pid_count - 5
        for _ in range(5):
            child_child.add_node(
                "node", tme=0, pid=pid_count, ppid=ppid, exit_tme=0)
            pid_count += 1

        pid_count = 1
        self.modified_prototype_skipped = Prototype()
        root = self.modified_prototype_skipped.add_node(
            "root", tme=0, pid=1, ppid=0, exit_tme=0)
        pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        for _ in range(10):
            root.add_node("child2", tme=0, pid=pid_count, ppid=1, exit_tme=0)
            pid_count += 1
        child = list(root.children())[1]
        for i in range(10):
            child.add_node(str(i), tme=0, pid=pid_count, ppid=3, exit_tme=0)
            pid_count += 1

    def test_start_tree(self):
        algorithm = IncrementalDistanceAlgorithm()
        algorithm.prototypes = [simple_prototype()]
        with self.assertRaises(TreeNotStartedException):
            algorithm.add_event(ProcessStartEvent(0, 1, 0, name="root"))

    def _add_events(self, algorithm=None, events=None):
        algorithm.start_tree()
        for event in events.event_iter(supported=algorithm.supported):
            try:
                result = algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        return result

    def _test_signature(self, algorithm=None, signature=None, events=None,
                        prototype=None):
        if prototype is None:
            prototype = self.prototype
        signature = signature()
        algorithm = algorithm(signature=signature)
        algorithm.prototypes = [prototype]

        return self._add_events(algorithm=algorithm, events=events)[-1]

    def _test_symmetry(self, algorithm=None, signature=None, prototype=None,
                       tree=None):
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
        return algorithm.prototype_node_counts(signature=True)

    def test_prototype_count_no_signature(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(signature=signature)
        algorithm.prototypes = [self.prototype]
        # test first ensemble, first prototype
        self.assertEqual(algorithm.prototype_node_counts(
            signature=False)[0][0], 56)

    def test_node_count_no_signature(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(signature=signature)
        algorithm.prototypes = [self.prototype]

        algorithm.start_tree()
        for event in Event.from_tree(self.prototype, supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        self.assertEqual(algorithm.tree_node_counts(signature=False)[0], 56)
        algorithm.finish_tree()

    def test_distance_zero(self):
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.prototype
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.prototype
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.prototype
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.prototype
            )[0], [0])

    def test_another_child(self):
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_position
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_position
            )[0], [30])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_position
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_position
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_position
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_position
            )[0], [34])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_position
            )[0], [40])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_position
            )[0], [46])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_position
            )[0], [50])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=10),
                events=self.modified_prototype_position
            )[0], [70])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=100),
                events=self.modified_prototype_position
            )[0], [430])

    def test_another_child2(self):
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_position2
            )[0], [22])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_position2
            )[0], [30])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_position2
            )[0], [22])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_position2
            )[0], [22])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_position2
            )[0], [28])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_position2
            )[0], [34])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_position2
            )[0], [40])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_position2
            )[0], [46])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_position2
            )[0], [50])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=10),
                events=self.modified_prototype_position2
            )[0], [70])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=100),
                events=self.modified_prototype_position2
            )[0], [430])

    def test_another_name(self):
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_name
            )[0], [1])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_name
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_name
            )[0], [2])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_name
            )[0], [1])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_name
            )[0], [4])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_name
            )[0], [7])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_name
            )[0], [10])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_name
            )[0], [13])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_name
            )[0], [16])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=6),
                events=self.modified_prototype_name
            )[0], [19])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=7),
                events=self.modified_prototype_name
            )[0], [22])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8),
                events=self.modified_prototype_name
            )[0], [25])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=9),
                events=self.modified_prototype_name
            )[0], [28])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=10),
                events=self.modified_prototype_name
            )[0], [30])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=11),
                events=self.modified_prototype_name
            )[0], [33])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=12),
                events=self.modified_prototype_name
            )[0], [36])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=13),
                events=self.modified_prototype_name
            )[0], [39])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=14),
                events=self.modified_prototype_name
            )[0], [42])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=15),
                events=self.modified_prototype_name
            )[0], [45])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=16),
                events=self.modified_prototype_name
            )[0], [48])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=17),
                events=self.modified_prototype_name
            )[0], [51])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=18),
                events=self.modified_prototype_name
            )[0], [54])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=19),
                events=self.modified_prototype_name
            )[0], [57])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=20),
                events=self.modified_prototype_name
            )[0], [60])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=100),
                events=self.modified_prototype_name
            )[0], [220])  # TODO: check

    def test_another_frequency(self):
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_frequency
            )[0], [0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_frequency
            )[0], [2])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderByNameTopologySignature(),
                events=self.modified_prototype_frequency
            )[0], [0])
        for i in range(10):
            self.assertEqual(
                [0],
                self._test_signature(
                    algorithm=IncrementalDistanceAlgorithm,
                    signature=lambda: ParentCountedChildrenByNameTopologySignature(
                        count=i),
                    events=self.modified_prototype_frequency
                )[0])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=10),
                events=self.modified_prototype_frequency
            )[0], [1])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=11),
                events=self.modified_prototype_frequency
            )[0], [4])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=12),
                events=self.modified_prototype_frequency
            )[0], [6])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=13),
                events=self.modified_prototype_frequency
            )[0], [8])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=14),
                events=self.modified_prototype_frequency
            )[0], [10])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=15),
                events=self.modified_prototype_frequency
            )[0], [12])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=16),
                events=self.modified_prototype_frequency
            )[0], [14])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=18),
                events=self.modified_prototype_frequency
            )[0], [18])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=19),
                events=self.modified_prototype_frequency
            )[0], [20])  # TODO: check
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=20),
                events=self.modified_prototype_frequency
            )[0], [22])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=21),
                events=self.modified_prototype_frequency
            )[0], [24])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=22),
                events=self.modified_prototype_frequency
            )[0], [26])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=23),
                events=self.modified_prototype_frequency
            )[0], [28])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=24),
                events=self.modified_prototype_frequency
            )[0], [30])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=25),
                events=self.modified_prototype_frequency
            )[0], [32])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=26),
                events=self.modified_prototype_frequency
            )[0], [34])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=27),
                events=self.modified_prototype_frequency
            )[0], [36])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=28),
                events=self.modified_prototype_frequency
            )[0], [38])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=29),
                events=self.modified_prototype_frequency
            )[0], [40])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=30),
                events=self.modified_prototype_frequency
            )[0], [42])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=31),
                events=self.modified_prototype_frequency
            )[0], [44])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=100),
                events=self.modified_prototype_frequency
            )[0], [182])

    def test_another_skipped(self):
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_skipped
            )[0], [1])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildOrderTopologySignature(),
                events=self.modified_prototype_skipped
            )[0], [5])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentChildByNameTopologySignature(),
                events=self.modified_prototype_skipped
            )[0], [1])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0),
                events=self.modified_prototype_skipped
            )[0], [1])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1),
                events=self.modified_prototype_skipped
            )[0], [3])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2),
                events=self.modified_prototype_skipped
            )[0], [5])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3),
                events=self.modified_prototype_skipped
            )[0], [7])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4),
                events=self.modified_prototype_skipped
            )[0], [9])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5),
                events=self.modified_prototype_skipped
            )[0], [10])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=10),
                events=self.modified_prototype_skipped
            )[0], [15])
        self.assertEqual(
            self._test_signature(
                algorithm=IncrementalDistanceAlgorithm,
                signature=lambda: ParentCountedChildrenByNameTopologySignature(
                    count=100),
                events=self.modified_prototype_skipped
            )[0], [105])

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
        )[0][0], 14)  # first ensemble, first prototype
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderTopologySignature()
        )[0], [56])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentChildOrderByNameTopologySignature()
        )[0], [16])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=0)
        )[0], [14])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=1)
        )[0], [21])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=2)
        )[0], [28])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=3)
        )[0], [35])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=4)
        )[0], [42])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=5)
        )[0], [48])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=6)
        )[0], [54])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=7)
        )[0], [60])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=8)
        )[0], [66])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=9)
        )[0], [72])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=10)
        )[0], [76])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=11)
        )[0], [80])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=12)
        )[0], [84])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=13)
        )[0], [88])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=14)
        )[0], [92])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=15)
        )[0], [96])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=16)
        )[0], [100])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=17)
        )[0], [104])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=18)
        )[0], [108])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=19)
        )[0], [112])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=20)
        )[0], [116])
        self.assertEqual(self._test_prototype_count(
            algorithm=IncrementalDistanceAlgorithm,
            signature=lambda: ParentCountedChildrenByNameTopologySignature(count=100)
        )[0], [356])

    def test_representation(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [self.prototype]
        algorithm.start_tree()
        self.assertEqual(
            algorithm.__repr__(),
            "IncrementalDistanceAlgorithm (cache_statistics=SplittedStatistics, "
            "distance=SimpleDistance, supported=['ProcessStartEvent', "
            "'ProcessExitEvent'])")

    def test_traffic_event(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [self.prototype]

        algorithm.start_tree()
        self.assertRaises(
            EventNotSupportedException,
            algorithm.add_event,
            TrafficEvent(tme=0, pid=2, ppid=1, value=0.5)
        )
        algorithm.finish_tree()

    def test_none_event(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [self.prototype]

        algorithm.start_tree()
        self.assertRaises(EventNotSupportedException, algorithm.add_event, None)
        algorithm.finish_tree()

    def test_format_tree_node_counts(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]

        algorithm.start_tree()
        self.assertEqual([], algorithm.tree_node_counts(signature=False))
        # FIXME: I might expect [] here, because it is not initialised
        self.assertEqual([0], algorithm.tree_node_counts(signature=True))
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([4], algorithm.tree_node_counts(signature=False))
        self.assertEqual([3], algorithm.tree_node_counts(signature=True))

    def test_format_prototype_node_counts(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]

        self.assertEqual([[5]], algorithm.prototype_node_counts(signature=False))
        self.assertEqual([[3]], algorithm.prototype_node_counts(signature=True))

        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        self.assertEqual([[5, 4]], algorithm.prototype_node_counts(signature=False))
        self.assertEqual([[3, 3]], algorithm.prototype_node_counts(signature=True))

    def test_format_prototype_event_counts(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]
        self.assertEqual([[3]], algorithm.prototype_event_counts())

        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]
        self.assertEqual([[3, 3]], algorithm.prototype_event_counts())

    def test_format_event_counts(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]

        algorithm.start_tree()
        for event in Event.from_tree(simple_prototype(), supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[3]], algorithm.event_counts())

        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        algorithm.start_tree()
        for event in Event.from_tree(simple_prototype(), supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[3, 3]], algorithm.event_counts())

    def test_format_add_event(self):
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]

        algorithm.start_tree()
        base_distance = 2
        for event in Event.from_tree(simple_prototype(), supported={ProcessStartEvent: True}):
            self.assertEqual([[base_distance]], algorithm.add_event(event)[0])
            if base_distance > 0:
                base_distance -= 1
        algorithm.finish_tree()

        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        algorithm.start_tree()
        base_distance = 2
        for event in Event.from_tree(simple_prototype(), supported={ProcessStartEvent: True}):
            self.assertEqual(
                [[base_distance, base_distance]], algorithm.add_event(event)[0])
            if base_distance > 0:
                base_distance -= 1
        algorithm.finish_tree()

    def test_ensemble_format_tree_node_counts(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderByNameTopologySignature()])
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]

        algorithm.start_tree()
        self.assertEqual([], algorithm.tree_node_counts(signature=False))
        self.assertEqual([0, 0], algorithm.tree_node_counts(signature=True))
        for event in Event.from_tree(simple_monitoring_tree(), supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([4, 4], algorithm.tree_node_counts(signature=False))
        self.assertEqual([3, 3], algorithm.tree_node_counts(signature=True))

    def test_ensemble_format_prototype_node_counts(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderByNameTopologySignature()])
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]

        self.assertEqual([[5], [5]], algorithm.prototype_node_counts(signature=False))
        self.assertEqual([[3], [5]], algorithm.prototype_node_counts(signature=True))

        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        self.assertEqual(
            [[5, 4], [5, 4]], algorithm.prototype_node_counts(signature=False))
        self.assertEqual(
            [[3, 3], [5, 3]], algorithm.prototype_node_counts(signature=True))

    def test_ensemble_format_prototype_event_counts(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderByNameTopologySignature()])
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]
        self.assertEqual([[3], [5]], algorithm.prototype_event_counts())

        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]
        self.assertEqual([[3, 3], [5, 3]], algorithm.prototype_event_counts())

    def test_ensemble_format_event_counts(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderByNameTopologySignature()])
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature, distance=SimpleDistance)
        algorithm.prototypes = [simple_prototype()]

        algorithm.start_tree()
        for event in Event.from_tree(simple_prototype(), supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[3], [5]], algorithm.event_counts())

        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]

        algorithm.start_tree()
        for event in Event.from_tree(simple_prototype(), supported={ProcessStartEvent: True}):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual([[3, 3], [5, 5]], algorithm.event_counts())
