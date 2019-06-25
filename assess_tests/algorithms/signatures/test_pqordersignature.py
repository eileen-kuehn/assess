import unittest

from assess.algorithms.signatures.pqordersignature import PQOrderSignature
from assess_tests.basedata import simple_prototype


class TestPQOrderSignature(unittest.TestCase):
    def test_base_pqorder_signature(self):
        signature = PQOrderSignature()
        signatures = set()
        p_signatures = set()
        prototype = simple_prototype()
        for node in prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
            p_signatures.add(signature.get_signature(node, node.parent(), dimension="p"))
        self.assertEqual(4, len(signatures))
        self.assertEqual(3, len(p_signatures))
        self.assertNotEqual(signatures, p_signatures)

    def test_longer_pqorder_signature(self):
        signature = PQOrderSignature(width=2)
        signatures = set()
        prototype = simple_prototype()
        for node in prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        print(signatures)
