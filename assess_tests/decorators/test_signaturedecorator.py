import unittest

from assess.algorithms.signatures.signatures import \
    ParentChildByNameTopologySignature, ParentChildOrderByNameTopologySignature
from assess.decorators.signaturedecorator import SignatureDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.events.events import Event

from assess_tests.basedata import simple_prototype, simple_monitoring_tree


class TestSignatureDecorator(unittest.TestCase):
    def test_creation(self):
        decorator = SignatureDecorator()
        self.assertEqual(decorator._name, "signature")
        self.assertEqual(decorator.data(), [])
        self.assertEqual(decorator.descriptive_data(), {"signature": []})

    def test_signatures(self):
        decorator = SignatureDecorator()
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildByNameTopologySignature())
        algorithm.prototypes = [simple_prototype()]
        decorator.wrap_algorithm(algorithm)

        decorator.start_tree()
        self.assertEqual(decorator.descriptive_data(), {"signature": [[[]]]})
        decorator.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {"signature": [[[]]]})

        decorator.wrap_algorithm(algorithm)
        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["signature"]), 1)
        self.assertEqual(len(set(description["signature"][0][0])), 3)
        self.assertEqual(len(description["signature"][0][0]), 4)
        self.assertEqual(description["signature"][0][0][0], "root_1")
        self.assertEqual(description["signature"][0][0][1], "test_149160533")
        self.assertEqual(description["signature"][0][0][3], "muh_149160533")

        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["signature"]), 2)

    def test_ensemble_signature(self):
        decorator = SignatureDecorator()
        algorithm = IncrementalDistanceAlgorithm(
            signature=EnsembleSignature(
                signatures=[ParentChildByNameTopologySignature(),
                            ParentChildOrderByNameTopologySignature()])
        )
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {'signature': [[[
            'root_1',
            'test_149160533',
            'test_149160533',
            'muh_149160533'
        ], [
            '.0_root_1',
            '.0.0_test_245236498',
            '.0.0_test_245236498',
            '.0.1_muh_245236498']]]})

        algorithm.start_tree()
        for event in Event.from_tree(simple_prototype()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {'signature': [[[
            'root_1',
            'test_149160533',
            'test_149160533',
            'muh_149160533'
        ], [
            '.0_root_1',
            '.0.0_test_245236498',
            '.0.0_test_245236498',
            '.0.1_muh_245236498'
        ]], [[
            'root_1',
            'test_149160533',
            'muh_149160533',
            'test_149160533',
            'muh_149160533'
        ], [
            '.0_root_1',
            '.0.0_test_245236498',
            '.0.1_muh_245236498',
            '.0.2_test_245236498',
            '.0.3_muh_245236498']]]})
