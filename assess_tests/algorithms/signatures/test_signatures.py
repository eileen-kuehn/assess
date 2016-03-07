import unittest

from assess.algorithms.signatures.signatures import *
from assess.prototypes.simpleprototypes import Prototype


class TestSignatureFunctionalities(unittest.TestCase):
    def setUp(self):
        self.prototype = Prototype()
        root = self.prototype.add_node("root", ppid=0, pid=1)
        for i in range(10):
            root.add_node("child")
        for i in range(10):
            root.add_node("child2")
        for i in range(10):
            root.add_node("child")
        for i in range(10):
            root.add_node("child2")
        child_node = list(root.children())[2]
        for i in range(10):
            child_node.add_node(i)
        child_child_node = list(child_node.children())[0]
        for i in range(5):
            child_child_node.add_node("child")

    def test_base_signature(self):
        signature = Signature()
        self._initialize_signature(signature)

        # check that node count is still the same like in original tree
        signatures = set()
        for node in self.prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        # TODO: is this really correct?
        #self.assertEqual(len(signatures), self.prototype.node_count())
        self.assertEqual(len(signatures), 13)

    def test_parent_child_by_name_topology_signature(self):
        signature = ParentChildByNameTopologySignature()
        self._initialize_signature(signature)

        # ensure that "same nodes" get same signature
        root = self.prototype.root()
        node_signature = None
        signatures = set()
        for child in root.children():
            signatures.add(signature.get_signature(child, root))
        self.assertEqual(len(signatures), 2)

        child_node = list(root.children())[2]
        signatures = set()
        for child in child_node.children():
            signatures.add(signature.get_signature(child, child_node))
        self.assertEqual(len(signatures), 10)

        # test if there are "just" 13 different signatures
        signatures = set()
        for node in self.prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), 14)

    def test_parent_child_order_topology_signature(self):
        signature = ParentChildOrderTopologySignature()
        self._initialize_signature(signature)

        # all nodes should have different names
        signatures = set()
        for node in self.prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), len(list(self.prototype.nodes())))

    def test_parent_child_order_by_name_topology_signature(self):
        signature = ParentChildOrderByNameTopologySignature()
        self._initialize_signature(signature)

        signatures = set()
        for node in self.prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), 16)

    def test_parent_counted_children_by_name_topology_signature(self):
        max = self.prototype.node_count()

        # should match by name signatures
        self._check_counted_signature(0, 14)

        self._check_counted_signature(1, 18)
        self._check_counted_signature(2, 22)
        self._check_counted_signature(3, 26)
        self._check_counted_signature(4, 30)
        self._check_counted_signature(5, 33)
        self._check_counted_signature(6, 36)
        self._check_counted_signature(7, 39)
        self._check_counted_signature(8, 42)
        self._check_counted_signature(9, 45)
        self._check_counted_signature(10, 46)
        self._check_counted_signature(11, 47)
        self._check_counted_signature(12, 48)
        self._check_counted_signature(13, 49)
        self._check_counted_signature(14, 50)
        self._check_counted_signature(15, 51)
        self._check_counted_signature(20, max)
        self._check_counted_signature(21, max)
        self._check_counted_signature(50, max)
        self._check_counted_signature(100, max)

    def _check_counted_signature(self, count, result):
        signature = ParentCountedChildrenByNameTopologySignature(count=count)
        self._initialize_signature(signature)

        signatures = set()
        for node in self.prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), result)

    def _initialize_signature(self, signature):
        for node in self.prototype.nodes():
            self.assertIsNotNone(signature.get_signature(node, node.parent()))
