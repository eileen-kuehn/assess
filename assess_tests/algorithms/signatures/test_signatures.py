import unittest

from assess.algorithms.signatures.signatures import *
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.prototypes.simpleprototypes import Prototype
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.decorators.datadecorator import DataDecorator
from assess.exceptions.exceptions import EventNotSupportedException
from assess.algorithms.distances.simpledistance import SimpleDistance

from assess_tests.basedata import simple_prototype, real_tree


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
            current_signature = signature.get_signature(child, root)
            signatures.add(current_signature)
            self.assertEqual(current_signature,
                             ParentChildByNameTopologySignature.signature_string(
                                 child.name,
                                 signature.get_signature(root, None) if root is not None else ""))
        self.assertEqual(len(signatures), 2)

        child_node = list(root.children())[2]
        signatures = set()
        for child in child_node.children():
            current_signature = signature.get_signature(child, child_node)
            signatures.add(current_signature)
            self.assertEqual(current_signature,
                             ParentChildByNameTopologySignature.signature_string(
                                 child.name,
                                 signature.get_signature(child_node, None) if child_node is not None else ""))
        self.assertEqual(len(signatures), 10)

        # test if there are "just" 13 different signatures
        signatures = set()
        for node in self.prototype.nodes():
            current_signature = signature.get_signature(node, node.parent())
            signatures.add(current_signature)
            self.assertEqual(current_signature,
                             ParentChildByNameTopologySignature.signature_string(
                                 node.name,
                                 signature.get_signature(node.parent(), None) if node.parent() is not None else ""))
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

    def test_representation(self):
        signature = ParentCountedChildrenByNameTopologySignature(count=5)
        self.assertEqual(signature.__repr__(), "ParentCountedChildrenByNameTopologySignature (count: 5)")

    def test_custom_creation(self):
        signature = Signature()
        self.assertEqual(Signature, signature.__class__)
        signature = Signature("ParentChildByNameTopologySignature")
        self.assertEqual(ParentChildByNameTopologySignature, signature.__class__)
        signature = Signature("ParentChildOrderTopologySignature")
        self.assertEqual(ParentChildOrderTopologySignature, signature.__class__)
        signature = Signature("ParentChildOrderByNameTopologySignature")
        self.assertEqual(ParentChildOrderByNameTopologySignature, signature.__class__)

    def test_empty_nodes(self):
        signature = ParentCountedChildrenByNameTopologySignature(count=2)

        signatures = set()
        for node in simple_prototype().nodes(include_marker=True):
            try:
                signatures.add(signature.get_signature(node, node.parent()))
            except AttributeError:
                signatures.update(signature.finish_node(node.parent()))
        print(signatures)
        self.assertEqual(
            set({'_root_1', '_test_192807604', 'muh__192807604', 'muh_test__192807604',
                 'muh_test_muh_192807604', 'test_muh_192807604',
                 'test_muh_test_192807604'}), signatures)

    def test_count_signature_for_correct_zero_distance(self):
        signature = ParentCountedChildrenByNameTopologySignature(count=3)
        algorithm = IncrementalDistanceAlgorithm(signature=signature)
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)
        algorithm.prototypes = [real_tree()]

        algorithm.start_tree()
        for event in real_tree().event_iter(include_marker=True):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        print(algorithm._signature_prototypes._prototype_dict[0]._prototype_dict.keys())
        self.assertEqual([[[0]]], decorator.data())

    def test_node_count_for_correct_zero_distance(self):
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature(),
                                                  ParentCountedChildrenByNameTopologySignature(count=3)])
        algorithm = IncrementalDistanceAlgorithm(signature=signature, distance=SimpleDistance)
        data_decorator = DataDecorator()
        data_decorator.wrap_algorithm(algorithm)
        algorithm.prototypes = [real_tree()]

        algorithm.start_tree()
        for event in real_tree().event_iter(include_marker=True):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        self.assertEqual([tree_value for values in data_decorator.data().get("prototypes", {}).get("converted", []) for tree_value in values],
                         [tree_value for values in data_decorator.data().get("monitoring", {}).get("converted", []) for tree_value in values])

