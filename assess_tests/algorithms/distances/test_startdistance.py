import unittest

from assess.algorithms.distances.startdistance import StartDistance
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import *

from assess_tests.basedata import simple_prototype, simple_monitoring_tree, \
    simple_repeated_monitoring_tree


class TestStartDistance(unittest.TestCase):
    def test_simple(self):
        algorithm = IncrementalDistanceAlgorithm(signature=ParentChildByNameTopologySignature())
        algorithm.prototypes = [simple_prototype()]
        distance = StartDistance(algorithm=algorithm)
        distance.init_distance()

        for index, dist in enumerate(distance):
            self.assertEqual(dist, 5)
        self.assertEqual(index, 0)
        self.assertTrue(distance.is_prototype_based_on_original())

        for node in simple_monitoring_tree().nodes():
            node_signature = algorithm.signature.get_signature(node, node.parent())
            distance.update_distance(
                signature=node_signature,
                value=float(node.exit_tme)-float(node.tme),
                matching_prototypes=algorithm.signature_prototypes.get(signature=node_signature)
            )
        self.assertEqual(distance._monitoring_results_dict[algorithm.prototypes[0]], 1)
        result = distance._monitoring_results_dict
        distance.finish_distance()
        self.assertEqual(result, distance._monitoring_results_dict)

    def test_repeated(self):
        algorithm = IncrementalDistanceAlgorithm(signature=ParentChildByNameTopologySignature())
        algorithm.prototypes = [simple_prototype()]
        distance = StartDistance(algorithm=algorithm)
        distance.init_distance()

        for index, dist in enumerate(distance):
            self.assertEqual(dist, 5)
        self.assertEqual(index, 0)
        self.assertTrue(distance.is_prototype_based_on_original())

        for node in simple_repeated_monitoring_tree().nodes():
            node_signature = algorithm.signature.get_signature(node, node.parent())
            distance.update_distance(
                signature=node_signature,
                value=float(node.exit_tme)-float(node.tme),
                matching_prototypes=algorithm.signature_prototypes.get(signature=node_signature)
            )
        self.assertEqual(distance._monitoring_results_dict[algorithm.prototypes[0]], 4)
        result = distance._monitoring_results_dict
        distance.finish_distance()
        self.assertEqual(result, distance._monitoring_results_dict)
