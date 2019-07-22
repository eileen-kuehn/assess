import unittest

from assess.algorithms.distances.startdistance import StartDistance
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import \
    ParentChildByNameTopologySignature, ParentChildOrderByNameTopologySignature, \
    ParentCountedChildrenByNameTopologySignature
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.exceptions.exceptions import EventNotSupportedException

from assess_tests.basedata import simple_monitoring_tree, simple_prototype, real_tree

from treedistancegenerator.ted_generator import TEDGenerator
from treedistancegenerator.operations.random_operation import RandomOperation
from treedistancegenerator.costs.costs import TreeEditDistanceCost


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
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentChildOrderByNameTopologySignature()])
        self.assertEqual(2, signature.count)

        for node in simple_monitoring_tree().nodes():
            signature.prepare_signature(node, parent=node.parent())
        for node in simple_monitoring_tree().nodes():
            token = signature.get_signature(node, parent=node.parent())
            self.assertIsNotNone(token)
            self.assertEqual(2, len(token))
            self.assertIsNot(token[0], token[1])

    def test_empty_nodes(self):
        signature = EnsembleSignature(
            signatures=[ParentChildByNameTopologySignature(),
                        ParentCountedChildrenByNameTopologySignature(count=3)])
        algorithm = IncrementalDistanceAlgorithm(signature=signature)
        algorithm.prototypes = [simple_prototype()]

        algorithm.start_tree()
        for event in simple_monitoring_tree().event_iter():
            try:
                distance = algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        self.assertEqual([[0], [7]], distance[-1])

    def test_ensemble_result(self):
        """
        I recognised that apparently sometimes (or ever?) values of ensemble
        methods don't match results from single calculations. Therefore this
        test should uniquely test for this.
        """
        tree = real_tree()
        tree_generator = TEDGenerator(
            operation_generator=RandomOperation(
                insert_probability=.5, delete_probability=.5),
            costs=[TreeEditDistanceCost()],
            seed=1234)
        disturbed_tree = tree_generator.generate(tree)

        signatures = [ParentChildByNameTopologySignature(),
                      ParentCountedChildrenByNameTopologySignature(count=2)]
        # First test results from ensemble
        ensemble_signature = EnsembleSignature(signatures=signatures)
        decorator = DistanceMatrixDecorator(normalized=False)
        algorithm = IncrementalDistanceAlgorithm(
            signature=ensemble_signature,
            distance=StartDistance
        )
        decorator.wrap_algorithm(algorithm)
        algorithm.prototypes = [tree]

        algorithm.start_tree()
        for event in disturbed_tree.event_iter():
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        ensemble_data = decorator.data()

        # Second, validate this result with single measurements
        single_data = {}
        for index, signature in enumerate(signatures):
            decorator = DistanceMatrixDecorator(normalized=False)
            algorithm = IncrementalDistanceAlgorithm(
                signature=signature,
                distance=StartDistance
            )
            decorator.wrap_algorithm(algorithm)
            algorithm.prototypes = [real_tree()]
            algorithm.start_tree()
            for event in disturbed_tree.event_iter():
                try:
                    algorithm.add_event(event)
                except EventNotSupportedException:
                    pass
            algorithm.finish_tree()
            single_data[index] = decorator.data()
        for index, _ in enumerate(signatures):
            self.assertEqual(ensemble_data[0][index][0], single_data[index][0][0][0])
