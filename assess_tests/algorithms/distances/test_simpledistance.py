import unittest

from assess.algorithms.distances.simpledistance import *
from assess.algorithms.signatures.signaturecache import PrototypeSignatureCache
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.prototypes.simpleprototypes import Prototype, Tree


class TestSimpleDistance(unittest.TestCase):
    def setUp(self):
        self.prototype = Prototype()
        root = self.prototype.add_node("root", tme=0, exit_tme=3)
        root.add_node("test", tme=0, exit_tme=1)
        root.add_node("muh", tme=0, exit_tme=2)
        root.add_node("test", tme=1, exit_tme=2)
        root.add_node("muh", tme=1, exit_tme=3)

        self.test_tree = Tree()
        tree_root = self.test_tree.add_node("root", tme=0, exit_tme=3)
        tree_root.add_node("test", tme=0, exit_tme=1)
        tree_root.add_node("test", tme=1, exit_tme=2)
        tree_root.add_node("muh", tme=1, exit_tme=3)

    def test_creation2(self):
        signature = ParentChildByNameTopologySignature()
        distance = SimpleDistance2(prototypes=[self.prototype])
        signature_cache = self._create_signature_cache(
            self.prototype,
            signature
        )
        distance.init_distance(prototypes=[self.prototype], signature_prototypes=signature_cache)
        for index, dist in enumerate(distance):
            self.assertEqual(dist, 0)
        self.assertEqual(index, 0)
        self.assertFalse(distance.is_prototype_based_on_original())

        for node in self.test_tree.nodes():
            node_signature = signature.get_signature(node, node.parent())
            distance.update_distance(
                signature=node_signature,
                matching_prototypes=signature_cache.get(signature=node_signature),
                prototypes=[self.prototype],
                signature_prototypes=signature_cache
            )
        self.assertEqual(distance._monitoring_results_dict[self.prototype], 0)

        result = distance._monitoring_results_dict
        distance.finish_distance(prototypes=[self.prototype], signature_prototypes=signature_cache)
        self.assertEqual(result, distance._monitoring_results_dict)

    def test_creation(self):
        signature = ParentChildByNameTopologySignature()
        distance = SimpleDistance(prototypes=[self.prototype])
        signature_cache = self._create_signature_cache(
            self.prototype,
            signature
        )
        distance.init_distance(prototypes=[self.prototype], signature_prototypes=signature_cache)
        for index, dist in enumerate(distance):
            self.assertEqual(dist, 3)
        self.assertEqual(index, 0)
        self.assertFalse(distance.is_prototype_based_on_original())

        for node in self.test_tree.nodes():
            node_signature = signature.get_signature(node, node.parent())
            distance.update_distance(
                signature=node_signature,
                value=float(node.exit_tme)-float(node.tme),
                matching_prototypes=signature_cache.get(signature=node_signature),
                prototypes=[self.prototype],
                signature_prototypes=signature_cache
            )
        self.assertEqual(distance._monitoring_results_dict[self.prototype], 0)

        result = distance._monitoring_results_dict
        distance.finish_distance()
        self.assertEqual(result, distance._monitoring_results_dict)

    def _create_signature_cache(self, prototype, signature):
        signature_prototype = PrototypeSignatureCache()
        for node in self.prototype.nodes():
            node_signature = signature.get_signature(node, node.parent())
            signature_prototype.add_signature(
                signature=node_signature,
                prototype=prototype,
                value=(float(node.exit_tme)-float(node.tme))
            )
        return signature_prototype
