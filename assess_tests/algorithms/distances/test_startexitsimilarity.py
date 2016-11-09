import unittest

from assess.algorithms.distances.startexitsimilarity import StartExitSimilarity
from assess.algorithms.signatures.signatures import *
from assess_tests.algorithms.distances.test_distance import algorithm, monitoring_tree


class TestStartExitSimilarity(unittest.TestCase):
    def setUp(self):
        self.algorithm = algorithm(signature=ParentChildByNameTopologySignature())

    def test_creation(self):
        similarity = StartExitSimilarity(signature_count=self.algorithm.signature.count)
        similarity.init_distance()

        for index, dist in enumerate(similarity):
            self.assertEqual(dist, [0])
        self.assertEqual(index, 0)

    def test_base_similarity(self):
        similarity = StartExitSimilarity(signature_count=self.algorithm.signature.count)
        similarity.init_distance()

        for index, node in enumerate(monitoring_tree().nodes()):
            node_signature = self.algorithm.signature.get_signature(node, node.parent())
            matching_prototypes = self.algorithm.signature_prototypes.get(signature=[node_signature])
            similarity.update_distance(
                matches=[{token: matching_prototypes[index]} for index, token in
                         enumerate([node_signature])]
            )
        for result in similarity._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 4)
        similarity.update_distance(
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])]
        )
        for result in similarity._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 5)
        similarity.update_distance(
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])]
        )
        similarity.update_distance(
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])]
        )
        similarity.update_distance(
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])]
        )
        for result in similarity._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 7)
