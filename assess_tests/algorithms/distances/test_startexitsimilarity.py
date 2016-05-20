import unittest

from assess.algorithms.distances.startexitsimilarity import StartExitSimilarity
from assess.algorithms.signatures.signatures import *
from assess_tests.algorithms.distances.test_distance import algorithm, monitoring_tree


class TestStartExitSimilarity(unittest.TestCase):
    def setUp(self):
        self.algorithm = algorithm(signature=ParentChildByNameTopologySignature())

    def test_creation(self):
        similarity = StartExitSimilarity(algorithm=self.algorithm)
        similarity.init_distance()

        for index, dist in enumerate(similarity):
            self.assertEqual(dist, 0)
        self.assertEqual(index, 0)

    def test_base_similarity(self):
        similarity = StartExitSimilarity(algorithm=self.algorithm)
        similarity.init_distance()

        for index, node in enumerate(monitoring_tree().nodes()):
            node_signature = self.algorithm.signature.get_signature(node, node.parent())
            similarity.update_distance(
                signature=node_signature,
                matching_prototypes=self.algorithm.signature_prototypes.get(node_signature)
            )
        self.assertEqual(similarity._monitoring_results_dict[self.algorithm.prototypes[0]], 4)
        similarity.update_distance(
            signature=node_signature,
            matching_prototypes=self.algorithm.signature_prototypes.get(node_signature)
        )
        self.assertEqual(similarity._monitoring_results_dict[self.algorithm.prototypes[0]], 5)
        similarity.update_distance(
            signature=node_signature,
            matching_prototypes=self.algorithm.signature_prototypes.get(node_signature)
        )
        similarity.update_distance(
            signature=node_signature,
            matching_prototypes=self.algorithm.signature_prototypes.get(node_signature)
        )
        similarity.update_distance(
            signature=node_signature,
            matching_prototypes=self.algorithm.signature_prototypes.get(node_signature)
        )
        self.assertEqual(similarity._monitoring_results_dict[self.algorithm.prototypes[0]], 7)
