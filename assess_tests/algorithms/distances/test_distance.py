import unittest

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.events.events import ProcessExitEvent
from assess.prototypes.simpleprototypes import Prototype, Tree
from assess.algorithms.signatures.ensemblesignaturecache import \
    EnsemblePrototypeSignatureCache
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature


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
    signature_prototype = EnsemblePrototypeSignatureCache(
        supported={ProcessExitEvent: True})
    for node in prototype.nodes():
        node_signature = signature.get_signature(node, node.parent())
        signature_prototype[node_signature, prototype, ProcessExitEvent] = {
            "duration": (float(node.exit_tme) - float(node.tme))
        }
    return signature_prototype


class TestAlgorithm(object):
    pass


def algorithm(signature):
    test = TestAlgorithm()
    test.prototypes = [prototype()]
    test.signature_prototypes = prototype_signature(
        prototype=test.prototypes[0],
        signature=EnsembleSignature(signatures=[signature])
    )
    test.signature = signature
    return test


class TestDistance(unittest.TestCase):
    def test_creation(self):
        test_algorithm = algorithm(ParentChildByNameTopologySignature())
        test_algorithm.prototypes = ["1", "2", "3"]
        distance = Distance(
            signature_count=test_algorithm.signature.count)
        distance.init_distance(
            prototypes=test_algorithm.prototypes,
            signature_prototypes=test_algorithm.signature_prototypes
        )
        last_index = 0
        for index, dist in enumerate(distance.iter_on_prototypes(
                test_algorithm.prototypes)):
            self.assertEqual(dist, [0])
            last_index = index
        self.assertEqual(last_index, 2)
        self.assertEqual(distance.node_count(), [0])
        self.assertFalse(distance.is_prototype_based_on_original())

    def test_raises(self):
        distance = Distance()
        self.assertRaises(NotImplementedError, distance.update_distance, None, None)

    def test_adding_of_results(self):
        distance = Distance()
        self.assertEqual(
            distance._add_result_dicts(
                base=[{"1": 0, "2": 0}],
                to_add=[{"1": 1, "2": 1}]
            ), [{"1": 1, "2": 1}]
        )
        self.assertEqual(
            distance._add_result_dicts([{"1": 1, "2": 1}], [{"1": 2, "2": -1}]),
            [{"1": 3, "2": 0}]
        )
        self.assertEqual(
            distance._add_result_dicts([{"1": 1}], [{"2": 1}]),
            [{"1": 1, "2": 1}]
        )
        self.assertEqual(
            distance._add_result_dicts([{"1": 2, "2": 0}], [{"1": -1, "3": -.5}]),
            [{"1": 1, "2": 0, "3": -.5}]
        )
