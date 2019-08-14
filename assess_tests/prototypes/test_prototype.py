import unittest
import os
import assess_tests

from gnmutils.sources.filedatasource import FileDataSource

from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.prototypes.simpleprototypes import Prototype
from assess.exceptions.exceptions import TreeInvalidatedException, NodeNotEmptyException
from assess_tests.basedata import simple_prototype
from assess.events.events import ProcessExitEvent, ProcessStartEvent, Event, \
    ParameterEvent


class TestPrototypeFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_empty_tree(self):
        prototype = Prototype()
        self.assertEqual(prototype.node_count(), 0,
                         "The node count for an empty prototype should be 0")

    def test_empty_tree_root(self):
        prototype = Prototype()
        self.assertEqual(prototype.root(), None,
                         "The root of an empty prototype should be None")

    def test_invalid_tree(self):
        prototype = Prototype()
        prototype.add_node("test1")
        self.assertRaises(TreeInvalidatedException, prototype.add_node, "test2")

    def test_nodes_depth_first(self):
        nodes = []
        prototype = Prototype()
        root = prototype.add_node("root", pid=1, ppid=0)
        one = root.add_node("1")
        one_one = one.add_node("1.1")
        one_one_one = one_one.add_node("1.1.1")
        one_two = one.add_node("1.2")
        two = root.add_node("2")
        three = root.add_node("3")

        nodes.append(root)
        nodes.append(one)
        nodes.append(one_one)
        nodes.append(one_one_one)
        nodes.append(one_two)
        nodes.append(two)
        nodes.append(three)

        for node in prototype.nodes(depth_first=True):
            self.assertEqual(node, nodes.pop(0))
        self.assertEqual(len(nodes), 0)

    def test_nodes_width_first(self):
        nodes = []
        prototype = Prototype()
        root = prototype.add_node("root", pid=1, ppid=0)
        one = root.add_node("1")
        one_one = one.add_node("1.1")
        one_one_one = one_one.add_node("1.1.1")
        one_two = one.add_node("1.2")
        two = root.add_node("2")
        three = root.add_node("3")

        nodes.append(root)
        nodes.append(one)
        nodes.append(two)
        nodes.append(three)
        nodes.append(one_one)
        nodes.append(one_two)
        nodes.append(one_one_one)

        for node in prototype.nodes(depth_first=False):
            self.assertEqual(node, nodes.pop(0))
        self.assertEqual(len(nodes), 0)

    def test_tree_creation(self):
        prototype = Prototype()
        node_1 = prototype.add_node("node_1")
        self.assertEqual(
            node_1.name, "node_1", "The name of created node should be node_1")
        node_2 = prototype.add_node("node_2", node_1)
        self.assertEqual(
            node_2.name, "node_2", "The name of created node should be node_2")
        self.assertEqual(
            node_2.parent(), node_1, "The parent of node_2 should be node_1")
        node_3 = prototype.add_node("node_3", node_2)
        node_4 = prototype.add_node("node_4", node_2)
        self.assertEqual(
            node_1.child_count(), 1, "Node_1 should have only one child")
        self.assertEqual(
            node_2.child_count(), 2, "Node_2 should have two children")
        self.assertEqual(
            prototype.subtree_node_count(node_1), 4,
            "Subtree of node_1 should have 4 nodes")
        self.assertEqual(
            prototype.subtree_node_count(node_2), 3,
            "Subtree of node_2 should have 3 nodes")
        self.assertEqual(
            prototype.subtree_node_count(node_3), 1,
            "Subtree of node_3 should have 1 node")

        nodes = [node_1, node_2, node_3, node_4]
        self.assertEqual(len(list(prototype.nodes())), len(nodes))
        for node in prototype.nodes():
            self.assertTrue(node in nodes)

        self.assertEqual(
            prototype.subtree_node_count(prototype.root()), prototype.node_count())
        self.assertEqual(prototype.node_count(), 4)

    def test_node_properties(self):
        prototype = Prototype()
        root = prototype.add_node("root")
        first = prototype.add_node("first", root)
        second = prototype.add_node("second", first)
        second_2 = prototype.add_node("second_2", first)
        third = prototype.add_node("third", second)

        # test depth properties
        self.assertEqual(root.depth(), 0, "Depth of root should be 0")
        self.assertEqual(first.depth(), 1, "Depth of first should be 1")
        self.assertEqual(second.depth(), 2, "Depth of second should be 2")
        self.assertEqual(second_2.depth(), 2, "Depth of second_2 should be 2")
        self.assertEqual(third.depth(), 3, "Depth of third should be 3")

        # test parent properties
        self.assertEqual(third.parent(), second)
        self.assertEqual(second.parent(), first)
        self.assertEqual(second.parent(), second_2.parent())
        self.assertEqual(first.parent(), root)

        # test child count
        self.assertEqual(root.child_count(), 1)
        self.assertEqual(first.child_count(), 2)
        self.assertEqual(second.child_count(), 1)
        self.assertEqual(second_2.child_count(), 0)
        self.assertEqual(third.child_count(), 0)

        # test node number
        self.assertEqual(root.node_number(), 0)
        self.assertEqual(first.node_number(), 0)
        self.assertEqual(second.node_number(), 0)
        self.assertEqual(second_2.node_number(), 1)
        self.assertEqual(third.node_number(), 0)

    def test_node_order(self):
        prototype = Prototype()
        root = prototype.add_node("root")
        for i in range(20):
            prototype.add_node(name=i, parent=root)

        self.assertEqual(prototype.child_count(root), 20)
        # check order of nodes
        for node in prototype.children(root):
            self.assertEqual(
                prototype.node_number(node), int(node.name),
                "Number of node does not match")

    def test_creation_via_node(self):
        prototype = Prototype()
        root = prototype.add_node("root", pid=1, ppid=0)
        for i in range(20):
            root.add_node(i)

        self.assertEqual(root.child_count(), 20)
        for node in root.children():
            self.assertEqual(node.node_number(), int(node.name))

    def test_unique_tree_ids(self):
        prototype = Prototype()
        root = prototype.add_node("node", pid=1, ppid=0)
        for _ in range(20):
            root.add_node("node")
        one_child = list(root.children())[0]
        for _ in range(20):
            one_child.add_node("node")

        self.assertEqual(prototype.node_count(), 41)

    def test_parent(self):
        prototype = Prototype()
        root = prototype.add_node("root", pid=1, ppid=0)
        sub_root = root.add_node("sub_root", pid=2, ppid=1)
        sub_sub_root = sub_root.add_node("sub_sub_root", pid=3, ppid=2)

        self.assertEqual(root.parent(), None)
        self.assertEqual(prototype.parent(root), None)
        self.assertEqual(sub_root.parent(), root)
        self.assertEqual(prototype.parent(sub_root), root)
        self.assertEqual(sub_sub_root.parent(), sub_root)
        self.assertEqual(prototype.parent(sub_sub_root), sub_root)

    def test_children(self):
        prototype = simple_prototype()
        children = prototype.children_list(prototype.root())
        self.assertEqual(len(children), 4)
        self.assertEqual(len(prototype.children_list(children[0])), 0)

    def test_subtree_node_count(self):
        prototype = simple_prototype()
        self.assertEqual(prototype.subtree_node_count(), prototype.node_count())
        self.assertEqual(prototype.root().node_count(), prototype.node_count())
        self.assertEqual(
            prototype.subtree_node_count(prototype.children_list(prototype.root())[0]),
            1
        )

    def test_representation(self):
        prototype = simple_prototype()
        self.assertEqual(prototype.tree_repr(), "[root: [test, muh, test, muh]]")
        self.assertEqual(prototype.tree_repr(
            node_repr=lambda node: str(node.pid)), "[1: [2, 3, 4, 5]]")
        self.assertEqual(
            prototype.tree_repr(
                node_repr=lambda node: "%d (%d)" % (node.pid, node.ppid),
                sequence_fmt="(%s)"
            ), "(1 (0): (2 (1), 3 (1), 4 (1), 5 (1)))"
        )

    def test_global_order(self):
        prototype = Prototype()
        root = prototype.add_node("root")
        node_1 = prototype.add_node("node_1", parent=root)
        node_2 = prototype.add_node("node_2", parent=root)
        prototype.add_node("node_3", parent=node_2)
        prototype.add_node("node_4", parent=node_1)
        prototype.add_node("node_5", parent=node_2)
        prototype.add_node("node_6", parent=node_1)

        # test depth first
        self.assertEqual(
            [node.name for node in list(prototype.nodes())],
            ["root", "node_1", "node_4", "node_6", "node_2", "node_3", "node_5"])
        # test order first
        self.assertEqual(
            [node.name for node in list(prototype.nodes(order_first=True))],
            ["root", "node_1", "node_2", "node_3", "node_4", "node_5", "node_6"])
        # test linkage
        self.assertEqual(node_2.previous_node, node_1)
        self.assertEqual(node_2.next_node.name, "node_3")
        self.assertEqual(node_2.parent(), root)

    def test_from_job(self):
        file_path = os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/c01-007-102/1/1-process.csv"
        )
        data_source = FileDataSource()
        for job in data_source.jobs(path=file_path):
            prototype = Prototype.from_job(job)
        self.assertIsNotNone(prototype)
        self.assertEqual(prototype.node_count(), 9109)

        last_tme = 0
        for node in prototype.nodes(order_first=True):
            self.assertTrue(last_tme <= node.tme)
            last_tme = node.tme

    def test_node_removal(self):
        tree = Prototype()
        root = tree.add_node("root")
        node_1 = root.add_node("node_1")
        node_2 = root.add_node("node_2")
        node_3 = node_1.add_node("node_3")
        node_4 = node_3.add_node("node_4")
        node_5 = node_2.add_node("node_5")

        self.assertEqual(tree.node_count(), 6)
        self.assertRaises(NodeNotEmptyException, tree.remove_node, node_3)
        tree.remove_node(node=node_5)
        self.assertEqual(tree.node_count(), 5)
        # check correct order
        self.assertEqual(node_4, tree._graph._last_node)
        self.assertEqual(None, node_4.next_node)

        tree.remove_node(node=node_2)
        self.assertEqual(tree.node_count(), 4)
        self.assertEqual(node_1.next_node, node_3)
        self.assertEqual(node_3.previous_node, node_1)

        child_1 = node_3.add_node("child_1")
        child_2 = node_3.add_node("child_2")
        child_3 = node_3.add_node("child_3")
        self.assertEqual(node_4.position, 0)
        self.assertEqual(child_1.position, 1)
        self.assertEqual(child_2.position, 2)
        self.assertEqual(child_3.position, 3)
        tree.remove_node(node=child_2)
        self.assertEqual(child_1.position, 1)
        self.assertEqual(child_2.position, 2)

        tree.remove_subtree(node=node_3)
        self.assertEqual(tree.node_count(), 2)

    def test_to_index(self):
        prototype = simple_prototype()
        index = prototype.to_index(signature=ParentChildByNameTopologySignature())
        self.assertEqual(2, index.multiplicity(signature="root_1"))
        self.assertEqual(4, index.multiplicity(signature="test_149160533"))
        self.assertEqual(4, index.multiplicity(signature="muh_149160533"))
        self.assertEqual(3, index.node_count())
        self.assertEqual(2, index.get_statistics(
            signature="muh_149160533",
            key="duration",
            event_type=ProcessExitEvent)._statistics[1].mean)
        self.assertEqual(0, index.get_statistics(
            signature="muh_149160533",
            key="duration",
            event_type=ProcessExitEvent).distance(2))

        index = prototype.to_index(
            signature=ParentChildByNameTopologySignature(), supported={
                ProcessStartEvent: True,
                ProcessExitEvent: False
            })
        self.assertEqual(3, index.node_count())
        self.assertEqual(1, index.multiplicity(signature="root_1"))
        self.assertEqual(2, index.multiplicity(signature="test_149160533"))
        self.assertEqual(2, index.multiplicity(signature="muh_149160533"))

    def test_parent_child_event_iter(self):
        prototype = Prototype()
        root = prototype.add_node("root", pid=1, ppid=0, tme=0, exit_tme=3, traffic=[])
        one = root.add_node("one", pid=2, ppid=1, tme=0, exit_tme=2, traffic=[])
        one.add_node("one.one", pid=3, ppid=2, tme=1, exit_tme=2, traffic=[])
        one.add_node("one.two", pid=5, ppid=2, tme=2, exit_tme=2, traffic=[])
        root.add_node("two", pid=4, ppid=1, tme=1, exit_tme=2, traffic=[])
        finished = set()
        for event in prototype.event_iter(
                supported={
                    ProcessStartEvent: True,
                    ProcessExitEvent: True
                }):
            if isinstance(event, ProcessStartEvent):
                self.assertTrue(
                    event.ppid not in finished,
                    "Node with pid %s is already gone..." % event.ppid)
            if isinstance(event, ProcessExitEvent):
                self.assertTrue(
                    event.ppid not in finished,
                    "Node with pid %s has already been finished" % event.ppid)
                finished.add(event.pid)

    def test_streaming_order(self):
        prototype = Prototype()
        root = prototype.add_node("root", pid=2, ppid=1, tme=1, exit_tme=5)
        nodes = [root,
                 root.add_node("one", pid=3, ppid=2, tme=1, exit_tme=2),
                 root.add_node("two", pid=4, ppid=2, tme=1, exit_tme=2),
                 root.add_node("four", pid=5, ppid=2, tme=2, exit_tme=3),
                 root.add_node("three", pid=6, ppid=2, tme=1, exit_tme=3)]

        index = 0
        for event in prototype.event_iter(supported={ProcessStartEvent: True}):
            if isinstance(event, ProcessStartEvent):
                self.assertEquals(nodes[index].name, event.name)
                index += 1
        self.assertEquals(index, len(nodes))

    def test_parameter(self):
        prototype = Prototype()
        root = prototype.add_node("root", pid=1, test=2, muh=3, tme=3)
        self.assertEqual({"test": 2, "muh": 3}, root.parameters())

    def test_parameter_event_generation(self):
        prototype = Prototype()
        root = prototype.add_node("root", pid=1, ppid=0, test=2, muh=3, tme=3, exit_tme=3)
        events = 0
        matches = 0
        for event in Event.events_from_node(root, supported={ParameterEvent: True}):
            events += 1
            if event.name == "test":
                self.assertEqual(2, event.value)
                matches += 1
            if event.name == "muh":
                self.assertEqual(3, event.value)
                matches += 1
        self.assertEqual(2, events)
        self.assertEqual(2, matches)
