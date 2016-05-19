import unittest

from assess.algorithms.distances.additionalmissingdistance import AdditionalMissingDistance
from assess_tests.algorithms.distances.test_simpledistance import prototype, prototype_signature, \
    monitoring_tree
from assess.algorithms.signatures.signatures import *


class TestAdditionalMissingDistance(unittest.TestCase):
    # TODO: more tests need to be implemented
    def setUp(self):
        self.prototype = prototype()

    def test_creation(self):
        distance = AdditionalMissingDistance(prototypes=["1", "2"])
        distance.init_distance(prototypes=["1", "2"])

        for index, dist in enumerate(distance):
            self.assertEqual(dist, 0)
        self.assertEqual(index, 1)

    def test_distance(self):
        signature = ParentChildByNameTopologySignature()
        signature_cache = prototype_signature(prototype=self.prototype, signature=signature)

        distance = AdditionalMissingDistance(prototypes=[self.prototype])
        distance.init_distance(prototypes=[self.prototype], signature_prototypes=signature_cache)

        for node in monitoring_tree().nodes():
            node_signature = signature.get_signature(node, node.parent())
            distance.update_distance(
                signature=node_signature,
                matching_prototypes=signature_cache.get(node_signature),
                prototypes=[self.prototype],
                signature_prototypes=signature_cache
            )
        self.assertEqual(distance._monitoring_results_dict[self.prototype], 0)
        self.assertEqual(
            distance.finish_distance(prototypes=[self.prototype], signature_prototypes=signature_cache)[0],
            0
        )
