import unittest

from assess.prototypes.simpleprototypes import Prototype, Tree, Process
from assess.exceptions.exceptions import TreeInvalidatedException


class TestPrototypeFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_empty_tree(self):
        prototype = Prototype()
        self.assertEqual(prototype.node_count(), 0, "The node count for an empty prototype should be 0")

    def test_empty_tree_root(self):
        prototype = Prototype()
        self.assertEqual(prototype.root(), None, "The root of an empty prototype should be None")

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
        self.assertEqual(node_1.name, "node_1", "The name of created node should be node_1")
        node_2 = prototype.add_node("node_2", node_1)
        self.assertEqual(node_2.name, "node_2", "The name of created node should be node_2")
        self.assertEqual(node_2.parent(), node_1, "The parent of node_2 should be node_1")
        node_3 = prototype.add_node("node_3", node_2)
        node_4 = prototype.add_node("node_4", node_2)
        self.assertEqual(node_1.child_count(), 1, "Node_1 should have only one child")
        self.assertEqual(node_2.child_count(), 2, "Node_2 should have two children")
        self.assertEqual(prototype.subtree_node_count(node_1), 4, "Subtree of node_1 should have 4 nodes")
        self.assertEqual(prototype.subtree_node_count(node_2), 3, "Subtree of node_2 should have 3 nodes")
        self.assertEqual(prototype.subtree_node_count(node_3), 1, "Subtree of node_3 should have 1 node")

        nodes = [node_1, node_2, node_3, node_4]
        self.assertEqual(len(list(prototype.nodes())), len(nodes))
        for node in prototype.nodes():
            self.assertTrue(node in nodes)

        self.assertEqual(prototype.subtree_node_count(prototype.root()), prototype.node_count())
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
            self.assertEqual(prototype.node_number(node), int(node.name), "Number of node does not match")

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
        for i in range(20):
            root.add_node("node")
        one_child = list(root.children())[0]
        for i in range(20):
            one_child.add_node("node")

        self.assertEqual(prototype.node_count(), 41)
