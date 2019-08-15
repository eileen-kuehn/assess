import unittest

from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.algorithms.signatures.ensemblesignaturecache import \
    EnsembleSignatureCache, EnsemblePrototypeSignatureCache
from assess.algorithms.signatures.signatures import \
    ParentChildByNameTopologySignature, ParentChildOrderTopologySignature
from assess.events.events import ProcessStartEvent, ProcessExitEvent

from assess_tests.basedata import simple_unique_node_tree, simple_monitoring_tree


class TestEnsembleSignatureCache(unittest.TestCase):
    def test_creation(self):
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature()])
        cache = signature.signature_cache_class()
        self.assertTrue(isinstance(cache, EnsembleSignatureCache))

    def test_prototype_creation(self):
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature()])
        cache = signature.prototype_signature_cache_class()
        self.assertTrue(isinstance(cache, EnsemblePrototypeSignatureCache))

    def test_simple_cache(self):
        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature()])
        cache = signature.signature_cache_class()

        for node in simple_unique_node_tree().nodes():
            tokens = signature.get_signature(node, parent=node.parent())
            if not cache.node_count():
                # nothing added yet
                self.assertEqual([], cache.multiplicity(signature=tokens))
            else:
                self.assertEqual([0], cache.multiplicity(signature=tokens))
            cache[tokens, ProcessStartEvent] = {"value": 0}
            self.assertEqual([1], cache.multiplicity(signature=tokens))
        self.assertEqual([4], cache.node_count())
        self.assertEqual([4], cache.multiplicity())

        signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature()])
        cache = signature.signature_cache_class()

        for node in simple_monitoring_tree().nodes():
            cache[signature.get_signature(
                node, parent=node.parent()), ProcessStartEvent] = {"value": 0}
        self.assertEqual([3], cache.node_count())
        self.assertEqual([4], cache.multiplicity())

    def test_two_ensembles(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderTopologySignature()])
        cache = signature.signature_cache_class()

        for node in simple_unique_node_tree().nodes():
            tokens = signature.get_signature(node, parent=node.parent())
            if not cache.node_count():
                self.assertEqual([], cache.multiplicity(signature=tokens))
            else:
                self.assertEqual([0, 0], cache.multiplicity(signature=tokens))
            cache[tokens, ProcessStartEvent] = {"value": 0}
            self.assertEqual([1, 1], cache.multiplicity(signature=tokens))
        self.assertEqual([4, 4], cache.node_count())
        self.assertEqual([4, 4], cache.multiplicity())

    def test_two_ensembles_different_frequency(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderTopologySignature()])
        cache = signature.signature_cache_class()

        for node in simple_monitoring_tree().nodes():
            cache[signature.get_signature(
                node, parent=node.parent()), ProcessStartEvent] = {"value": 0}
        self.assertEqual([3, 4], cache.node_count())
        self.assertEqual([4, 4], cache.multiplicity())

    def test_simple_prototype_cache(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature()])
        cache = signature.prototype_signature_cache_class(
            supported={ProcessExitEvent: True})

        tree = simple_unique_node_tree()
        for node in tree.nodes():
            tokens = signature.get_signature(node, parent=node.parent())
            if not cache.node_count():
                # nothing added yet
                self.assertEqual([], cache.get(signature=tokens))
            else:
                self.assertTrue(isinstance(cache.get(signature=tokens)[0], dict))
            cache[tokens, tree, ProcessExitEvent] = {"value": 1}
            stats = cache.get_statistics(
                signature=tokens,
                prototype=tree,
                key="value",
                event_type=ProcessExitEvent
            )
            self.assertTrue(stats[0].count() >= 1)
        self.assertEqual([4], cache.node_count())
        self.assertEqual([4], cache.multiplicity())

        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature()])
        cache = signature.signature_cache_class()

        for node in simple_monitoring_tree().nodes():
            cache[signature.get_signature(
                node, parent=node.parent()), ProcessStartEvent] = {"value": 0}
        self.assertEqual([3], cache.node_count())
        self.assertEqual([4], cache.multiplicity())

    def test_two_prototype_ensembles(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderTopologySignature()])
        cache = signature.prototype_signature_cache_class()

        prototype = simple_unique_node_tree()
        for node in prototype.nodes():
            tokens = signature.get_signature(node, parent=node.parent())
            if not cache.node_count():
                self.assertEqual([], cache.get(signature=tokens))
            else:
                received = cache.get(signature=tokens)
                self.assertEqual(2, len(received))
                self.assertTrue(isinstance(received[0], dict))
            cache[tokens, prototype, ProcessStartEvent] = {"value": 1}
            received = cache.get(signature=tokens)
            self.assertEqual(2, len(received))
            self.assertTrue(isinstance(received[0], dict))
            self.assertTrue(
                received[0][prototype][ProcessStartEvent]["value"].count() >= 1)
        self.assertEqual([4, 4], cache.node_count())
        self.assertEqual([4, 4], cache.multiplicity())

    def test_two_prototype_ensembles_different_frequency(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderTopologySignature()])
        cache = signature.prototype_signature_cache_class(
            supported={ProcessExitEvent: True})

        prototype = simple_monitoring_tree()
        for node in prototype.nodes():
            cache[signature.get_signature(
                node, parent=node.parent()), prototype, ProcessExitEvent] = {
                "value": 1
            }
        self.assertEqual([3, 4], cache.node_count())
        self.assertEqual([4, 4], cache.multiplicity())
