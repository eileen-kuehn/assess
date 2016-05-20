import unittest

from assess.algorithms.distances.distance import Distance
from assess.prototypes.simpleprototypes import Prototype, Tree
from assess.algorithms.signatures.signaturecache import PrototypeSignatureCache
from assess.algorithms.signatures.signatures import *


def prototype():
    prototype_tree = Prototype()
    root = prototype_tree.add_node("root", tme=0, exit_tme=3)
    root.add_node("test", tme=0, exit_tme=1)
    root.add_node("muh", tme=0, exit_tme=2)
    root.add_node("test", tme=1, exit_tme=2)
    root.add_node("muh", tme=1, exit_tme=3)
    return prototype_tree


def monitoring_tree():
    test_tree = Tree()
    tree_root = test_tree.add_node("root", tme=0, exit_tme=3)
    tree_root.add_node("test", tme=0, exit_tme=1)
    tree_root.add_node("test", tme=1, exit_tme=2)
    tree_root.add_node("muh", tme=1, exit_tme=3)
    return test_tree


def additional_monitoring_tree():
    test_tree = Tree()
    tree_root = test_tree.add_node("root", tme=0, exit_tme=3)
    tree_root.add_node("hello", tme=0, exit_tme=2)
    tree_root.add_node("yes", tme=0, exit_tme=1)
    tree_root.add_node("test", tme=0, exit_tme=1)
    tree_root.add_node("muh", tme=0, exit_tme=2)
    tree_root.add_node("test", tme=1, exit_tme=3)
    return test_tree


def prototype_signature(prototype=None, signature=None):
    signature_prototype = PrototypeSignatureCache()
    for node in prototype.nodes():
        node_signature = signature.get_signature(node, node.parent())
        signature_prototype.add_signature(
            signature=node_signature,
            prototype=prototype,
            value=(float(node.exit_tme)-float(node.tme))
        )
    return signature_prototype


class TestAlgorithm(object):
    pass


def algorithm(signature):
    test = TestAlgorithm()
    test.prototypes = [prototype()]
    test.signature_prototypes = prototype_signature(
        prototype=test.prototypes[0],
        signature=signature
    )
    test.signature=signature
    return test


class TestDistance(unittest.TestCase):
    def test_creation(self):
        self.assertRaises(TypeError, Distance)
        test_algorithm = algorithm(ParentChildByNameTopologySignature())
        test_algorithm.prototypes = ["1", "2", "3"]
        distance = Distance(algorithm=test_algorithm)
        for index, dist in enumerate(distance):
            self.assertEqual(dist, 0)
        self.assertEqual(index, 2)
        self.assertEqual(distance.node_count(), 0)
        self.assertFalse(distance.is_prototype_based_on_original())

    def test_raises(self):
        distance = Distance(None)
        self.assertRaises(NotImplementedError, distance.update_distance)
        self.assertRaises(NotImplementedError, distance.finish_distance)

    def test_adding_of_results(self):
        distance = Distance(None)
        self.assertEqual(
            distance._add_result_dicts({"1": 0, "2": 0}, {"1": 1, "2": 1}),
            {"1": 1, "2": 1}
        )
        self.assertEqual(
            distance._add_result_dicts({"1": 1, "2": 1}, {"1": 2, "2": -1}),
            {"1": 3, "2": 0}
        )
        self.assertEqual(
            distance._add_result_dicts({"1": 1}, {"2": 1}),
            {"1": 1, "2": 1}
        )
        self.assertEqual(
            distance._add_result_dicts({"1": 2, "2": 0}, {"1": -1, "3": -.5}),
            {"1": 1, "2": 0, "3": -.5}
        )
