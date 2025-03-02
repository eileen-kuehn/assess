import unittest

from assess.algorithms.distances.startdistance import StartDistance
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.events.events import ProcessStartEvent

from assess_tests.basedata import simple_prototype, simple_monitoring_tree, \
    simple_repeated_monitoring_tree


class TestStartDistance(unittest.TestCase):
    def test_simple(self):
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildByNameTopologySignature(),
            distance=StartDistance)
        algorithm.prototypes = [simple_prototype()]
        distance = algorithm.distance
        distance.init_distance(
            prototypes=algorithm.prototypes,
            signature_prototypes=algorithm.signature_prototypes
        )

        last_index = 0
        for index, dist in enumerate(distance.iter_on_prototypes(algorithm.prototypes)):
            self.assertEqual(dist, [5])
            last_index = index
        self.assertEqual(last_index, 0)
        self.assertTrue(distance.is_prototype_based_on_original())

        for node in simple_monitoring_tree().nodes():
            node_signature = algorithm.signature.get_signature(node, node.parent())
            matching_prototypes = algorithm.signature_prototypes.get(
                signature=node_signature)
            distance.update_distance(
                prototypes=algorithm.prototypes,
                signature_prototypes=algorithm.signature_prototypes,
                matches=[{token: matching_prototypes[index]} for index, token in
                         enumerate(node_signature)],
                value=float(node.exit_tme) - float(node.tme),
            )
        for result in distance._monitoring_results_dict:
            self.assertEqual(result[algorithm.prototypes[0]], 1)
        result = distance._monitoring_results_dict
        distance.finish_distance(
            prototypes=algorithm.prototypes,
            signature_prototypes=algorithm.signature_prototypes
        )
        self.assertEqual(result, distance._monitoring_results_dict)

    def test_repeated(self):
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildByNameTopologySignature(),
            distance=StartDistance
        )
        distance = StartDistance(signature_count=algorithm.signature.count)
        algorithm.prototypes = [simple_prototype()]
        distance.init_distance(
            prototypes=algorithm.prototypes,
            signature_prototypes=algorithm.signature_prototypes
        )
        last_index = 0
        for index, dist in enumerate(distance.iter_on_prototypes(algorithm.prototypes)):
            self.assertEqual(dist, [5])
            last_index = index
        self.assertEqual(last_index, 0)
        self.assertTrue(distance.is_prototype_based_on_original())

        for node in simple_repeated_monitoring_tree().nodes():
            node_signature = algorithm.signature.get_signature(node, node.parent())
            matching_prototypes = algorithm.signature_prototypes.get(
                signature=node_signature)
            distance.update_distance(
                prototypes=algorithm.prototypes,
                signature_prototypes=algorithm.signature_prototypes,
                matches=[{token: matching_prototypes[index]} for index, token in
                         enumerate(node_signature)],
                value=float(node.exit_tme) - float(node.tme),
                event_type=ProcessStartEvent
            )
        for result in distance._monitoring_results_dict:
            self.assertEqual(result[algorithm.prototypes[0]], 4)
        result = distance._monitoring_results_dict
        distance.finish_distance(
            prototypes=algorithm.prototypes,
            signature_prototypes=algorithm.signature_prototypes
        )
        self.assertEqual(result, distance._monitoring_results_dict)
