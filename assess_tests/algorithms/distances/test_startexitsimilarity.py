import unittest

from assess.algorithms.distances.startexitsimilarity import StartExitSimilarity
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.events.events import ProcessStartEvent
from assess_tests.algorithms.distances.test_distance import algorithm, monitoring_tree


class TestStartExitSimilarity(unittest.TestCase):
    def setUp(self):
        self.algorithm = algorithm(signature=ParentChildByNameTopologySignature())

    def test_creation(self):
        similarity = StartExitSimilarity(
            signature_count=self.algorithm.signature.count)
        similarity.init_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes
        )

        last_index = 0
        for index, dist in enumerate(similarity.iter_on_prototypes(
                self.algorithm.prototypes)):
            self.assertEqual(dist, [0])
            last_index = index
        self.assertEqual(last_index, 0)

    def test_base_similarity(self):
        similarity = StartExitSimilarity(
            signature_count=self.algorithm.signature.count)
        similarity.init_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes
        )

        for index, node in enumerate(monitoring_tree().nodes()):
            node_signature = self.algorithm.signature.get_signature(node, node.parent())
            matching_prototypes = self.algorithm.signature_prototypes.get(
                signature=[node_signature])
            similarity.update_distance(
                prototypes=self.algorithm.prototypes,
                signature_prototypes=self.algorithm.signature_prototypes,
                matches=[{token: matching_prototypes[index]} for index, token in
                         enumerate([node_signature])],
                event_type=ProcessStartEvent
            )
        for result in similarity._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 4)
        similarity.update_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes,
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])],
            event_type=ProcessStartEvent
        )
        for result in similarity._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 5)
        similarity.update_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes,
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])],
            event_type=ProcessStartEvent
        )
        similarity.update_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes,
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])],
            event_type=ProcessStartEvent
        )
        similarity.update_distance(
            prototypes=self.algorithm.prototypes,
            signature_prototypes=self.algorithm.signature_prototypes,
            matches=[{token: matching_prototypes[index]} for index, token in
                     enumerate([node_signature])],
            event_type=ProcessStartEvent
        )
        for result in similarity._monitoring_results_dict:
            self.assertEqual(result[self.algorithm.prototypes[0]], 8)
