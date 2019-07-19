import unittest

from assess.algorithms.signatures.pqgramsignature import PQGramSignature

from assess_tests.basedata import simple_prototype


class TestPQGramSignatureFunctionalities(unittest.TestCase):
    def test_base_pqgram_signature(self):
        signature = PQGramSignature()
        signatures = set()
        prototype = simple_prototype()
        for node in prototype.nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), 3)

    def test_zero_pqgram_signature(self):
        signature = PQGramSignature(height=0, width=0)
        signatures = set()
        for node in simple_prototype().nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), 3)

    def test_similarity_name_signature(self):
        signature = PQGramSignature(height=1, width=0)
        signatures = set()
        for node in simple_prototype().nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), 3)

    def test_pggram_signature(self):
        signature = PQGramSignature(height=2, width=2)
        signatures = set()
        for node in simple_prototype().nodes():
            signatures.add(signature.get_signature(node, node.parent()))
        self.assertEqual(len(signatures), 5)

    def test_pqgram_empty_nodes(self):
        signature = PQGramSignature(height=2, width=2)
        signatures = set()
        for node in simple_prototype().nodes(include_marker=True):
            try:
                signatures.add(signature.get_signature(node, node.parent()))
            except AttributeError:
                signatures.update(signature.finish_node(node.parent()))
        self.assertEqual(
            {'__root__', 'root__test__', 'root__muh_test_', 'root__test_muh_test',
             'root__muh_test_muh', 'root___muh_test', 'root___muh'}, signatures)
