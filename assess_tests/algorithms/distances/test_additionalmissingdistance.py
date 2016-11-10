import unittest

from assess.algorithms.distances.additionalmissingdistance import AdditionalMissingDistance
from assess_tests.algorithms.distances.test_distance import monitoring_tree, algorithm, \
    additional_monitoring_tree
from assess.algorithms.signatures.signatures import *


class TestAdditionalMissingDistance(unittest.TestCase):
    # TODO: more tests need to be implemented
    def setUp(self):
        self.algorithm = algorithm(signature=ParentChildByNameTopologySignature())

    def test_creation(self):
        distance = AdditionalMissingDistance(signature_count=self.algorithm.signature.count)
        distance.init_distance(prototypes=self.algorithm.prototypes, signature_prototypes=self.algorithm.signature_prototypes)

        for index, dist in enumerate(distance.iter_on_prototypes(self.algorithm.prototypes)):
            self.assertEqual(dist, [0])
        self.assertEqual(index, 0)

    def test_distance(self):
        distance = AdditionalMissingDistance(signature_count=self.algorithm.signature.count)
        distance.init_distance(prototypes=self.algorithm.prototypes, signature_prototypes=self.algorithm.signature_prototypes)

        for node in monitoring_tree().nodes():
            node_signature = self.algorithm.signature.get_signature(node, node.parent())
            matching_prototypes = self.algorithm.signature_prototypes.get(signature=[node_signature])
            distance.update_distance(
                prototypes=self.algorithm.prototypes,
                signature_prototypes=self.algorithm.signature_prototypes,
                matches=[{token: matching_prototypes[index] for index, token in
                          enumerate([node_signature])}]
            )
        for result in distance._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 0)
        self.assertEqual(
            distance.finish_distance(
                prototypes=self.algorithm.prototypes,
                signature_prototypes=self.algorithm.signature_prototypes)[0],
            [0]
        )

    def test_additional_distance(self):
        distance = AdditionalMissingDistance(signature_count=self.algorithm.signature.count)
        distance.init_distance(prototypes=self.algorithm.prototypes, signature_prototypes=self.algorithm.signature_prototypes)

        for index, node in enumerate(additional_monitoring_tree().nodes()):
            node_signature = [self.algorithm.signature.get_signature(node, node.parent())]

            matching_prototypes = self.algorithm.signature_prototypes.get(signature=node_signature)
            distance.update_distance(
                prototypes=self.algorithm.prototypes,
                signature_prototypes=self.algorithm.signature_prototypes,
                matches=[{token: matching_prototypes[i]} for i, token in
                         enumerate(node_signature)]
            )
            for result in distance._monitoring_results_dict:
                self.assertEqual(result.values()[0], index*2 if index <= 2 else 4)
        self.assertEqual(distance._monitoring_results_dict[0][self.algorithm.prototypes[0]], 4)
        self.assertEqual(distance.finish_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes)[0], [2])
