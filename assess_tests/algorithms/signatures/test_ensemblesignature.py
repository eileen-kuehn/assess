import unittest

from assess.algorithms.signatures.signatures import *
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature

from assess_tests.basedata import simple_monitoring_tree


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
