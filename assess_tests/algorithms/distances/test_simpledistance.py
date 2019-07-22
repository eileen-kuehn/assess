import unittest

from assess.algorithms.distances.simpledistance import SimpleDistance2, SimpleDistance
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess_tests.algorithms.distances.test_distance import algorithm, monitoring_tree


class TestSimpleDistance(unittest.TestCase):
    def setUp(self):
        self.algorithm = algorithm(signature=ParentChildByNameTopologySignature())
        self.test_tree = monitoring_tree()

    def test_creation2(self):
        distance = SimpleDistance2(signature_count=self.algorithm.signature.count)
        distance.init_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes
        )
        last_index = 0
        for index, dist in enumerate(distance.iter_on_prototypes(
                self.algorithm.prototypes)):
            self.assertEqual(dist, [0])
            last_index = index
        self.assertEqual(last_index, 0)
        self.assertFalse(distance.is_prototype_based_on_original())

        for node in self.test_tree.nodes():
            node_signature = self.algorithm.signature.get_signature(
                node, node.parent())
            matching_prototypes = self.algorithm.signature_prototypes.get(
                signature=[node_signature])
            distance.update_distance(
                prototypes=self.algorithm.prototypes,
                signature_prototypes=self.algorithm.signature_prototypes,
                matches=[{token: matching_prototypes[index]} for index, token in
                         enumerate([node_signature])]
            )
        for result in distance._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 0)

        result = distance._monitoring_results_dict
        distance.finish_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes
        )
        self.assertEqual(result, distance._monitoring_results_dict)

    def test_creation(self):
        distance = SimpleDistance(
            signature_count=self.algorithm.signature.count)
        distance.init_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes
        )
        last_index = 0
        for index, dist in enumerate(
                distance.iter_on_prototypes(self.algorithm.prototypes)):
            self.assertEqual(dist, [3])
            last_index = index
        self.assertEqual(last_index, 0)
        self.assertFalse(distance.is_prototype_based_on_original())

        for node in self.test_tree.nodes():
            node_signature = self.algorithm.signature.get_signature(node, node.parent())
            matching_prototypes = self.algorithm.signature_prototypes.get(
                signature=[node_signature])
            distance.update_distance(
                prototypes=self.algorithm.prototypes,
                signature_prototypes=self.algorithm.signature_prototypes,
                matches=[{token: matching_prototypes[index]} for index, token in
                         enumerate([node_signature])],
                value=float(node.exit_tme) - float(node.tme),
            )
        for result in distance._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 0)

        result = distance._monitoring_results_dict
        distance.finish_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes)
        self.assertEqual(result, distance._monitoring_results_dict)
