import unittest

from assess.algorithms.signatures.signatures import *
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm

from assess_tests.basedata import simple_monitoring_tree, simple_prototype


class TestEnsembleSignature(unittest.TestCase):
    def test_simple_signature(self):
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature()])
        self.assertEqual(1, signature.count)

        for node in simple_monitoring_tree().nodes():
            signature.prepare_signature(node, parent=node.parent())
        for node in simple_monitoring_tree().nodes():
            token = signature.get_signature(node, parent=node.parent())
            self.assertIsNotNone(token)
            self.assertEqual(1, len(token))

    def test_two_signatures(self):
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature(), ParentChildOrderByNameTopologySignature()])
        self.assertEqual(2, signature.count)

        for node in simple_monitoring_tree().nodes():
            signature.prepare_signature(node, parent=node.parent())
        for node in simple_monitoring_tree().nodes():
            token = signature.get_signature(node, parent=node.parent())
            self.assertIsNotNone(token)
            self.assertEqual(2, len(token))
            self.assertIsNot(token[0], token[1])

    def test_empty_nodes(self):
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature(), ParentCountedChildrenByNameTopologySignature(count=2)])
        algorithm = IncrementalDistanceAlgorithm(signature=signature)
        algorithm.prototypes = [simple_prototype()]

        for event in simple_monitoring_tree().event_iter():
            distance = algorithm.add_event(event)
        self.assertEqual([[1], [7]], distance[-1])
