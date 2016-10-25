import unittest

from assess.decorators.signaturedecorator import SignatureDecorator
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import *
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
        algorithm = IncrementalDistanceAlgorithm(signature=ParentChildByNameTopologySignature())
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
        self.assertEqual(description["signature"][0][0][0], "root_-5995064038896156292")
        self.assertEqual(description["signature"][0][0][1], "test_703899357396914538")
        self.assertEqual(description["signature"][0][0][3], "muh_703899357396914538")

        decorator.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            decorator.add_event(event)
        decorator.finish_tree()
        description = decorator.descriptive_data()
        self.assertEqual(len(description["signature"]), 2)

    def test_ensemble_signature(self):
        decorator = SignatureDecorator()
        algorithm = IncrementalDistanceAlgorithm(
            signature=EnsembleSignature(signatures=[ParentChildByNameTopologySignature(),
                                                    ParentChildOrderByNameTopologySignature()]))
        algorithm.prototypes = [simple_prototype(), simple_monitoring_tree()]
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in Event.from_tree(simple_monitoring_tree()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {'signature': [[[
            'root_-5995064038896156292',
            'test_703899357396914538',
            'test_703899357396914538',
            'muh_703899357396914538'
        ], [
            '.0_root_-5995064038896156292',
            '.0.0_test_-1557915962781427776',
            '.0.0_test_-1557915962781427776',
            '.0.1_muh_-1557915962781427776']]]})

        algorithm.start_tree()
        for event in Event.from_tree(simple_prototype()):
            algorithm.add_event(event)
        algorithm.finish_tree()
        self.assertEqual(decorator.descriptive_data(), {'signature': [[[
            'root_-5995064038896156292',
            'test_703899357396914538',
            'test_703899357396914538',
            'muh_703899357396914538'
        ], [
            '.0_root_-5995064038896156292',
            '.0.0_test_-1557915962781427776',
            '.0.0_test_-1557915962781427776',
            '.0.1_muh_-1557915962781427776'
        ]], [[
            'root_-5995064038896156292',
            'test_703899357396914538',
            'muh_703899357396914538',
            'test_703899357396914538',
            'muh_703899357396914538'
        ], [
            '.0_root_-5995064038896156292',
            '.0.0_test_-1557915962781427776',
            '.0.1_muh_-1557915962781427776',
            '.0.2_test_-1557915962781427776',
            '.0.3_muh_-1557915962781427776']]]})

