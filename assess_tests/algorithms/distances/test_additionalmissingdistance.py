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
        distance = AdditionalMissingDistance(algorithm=self.algorithm)
        distance.init_distance()

        for index, dist in enumerate(distance):
            self.assertEqual(dist, 0)
        self.assertEqual(index, 0)

    def test_distance(self):
        distance = AdditionalMissingDistance(algorithm=self.algorithm)
        distance.init_distance()

        for node in monitoring_tree().nodes():
            node_signature = self.algorithm.signature.get_signature(node, node.parent())
            distance.update_distance(
                signature=node_signature,
                matching_prototypes=self.algorithm.signature_prototypes.get(node_signature)
            )
        self.assertEqual(distance._monitoring_results_dict[self.algorithm.prototypes[0]], 0)
        self.assertEqual(
            distance.finish_distance()[0],
            0
        )

    def test_additional_distance(self):
        distance = AdditionalMissingDistance(algorithm=self.algorithm)
        distance.init_distance()

        for index, node in enumerate(additional_monitoring_tree().nodes()):
            node_signature = self.algorithm.signature.get_signature(node, node.parent())
            distance.update_distance(
                signature=node_signature,
                matching_prototypes=self.algorithm.signature_prototypes.get(node_signature)
            )
            self.assertEqual(list(distance._monitoring_results_dict.values())[0], index*2 if index <= 2 else 4)
        self.assertEqual(distance._monitoring_results_dict[self.algorithm.prototypes[0]], 4)
        self.assertEqual(distance.finish_distance()[0], 2)
