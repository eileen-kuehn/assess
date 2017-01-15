import os
import unittest

import assess_tests
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.algorithms.distances.startexitdistance import StartExitDistance
from assess.algorithms.statistics.splittedstatistics import SplittedStatistics
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.exceptions.exceptions import EventNotSupportedException
from assess.generators.gnm_importer import CSVTreeBuilder
from assess.prototypes.simpleprototypes import Prototype


class TestComplexExamples(unittest.TestCase):
    def test_attribute_distance(self):
        tree_builder = CSVTreeBuilder()
        tree_1 = tree_builder.build(os.path.join(os.path.dirname(assess_tests.__file__),
                                                 "data/c01-007-102/2/1129-2-process.csv"))
        tree_2 = tree_builder.build(os.path.join(os.path.dirname(assess_tests.__file__),
                                                 "data/c01-007-102/2/1136-3-process.csv"))
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(signature=signature,
                                                 distance=lambda **kwargs: StartExitDistance(weight=0, **kwargs),
                                                 cache_statistics=SplittedStatistics)
        algorithm.prototypes = [tree_1, tree_2]
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in tree_1.event_iter():
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        algorithm.start_tree()
        for event in tree_2.event_iter():
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        data = decorator.data()
        print(decorator.data())
        self.assertEqual(4, abs(data[0][0][1]-data[1][0][0]))

    def test_symmetry_optimisation(self):
        tree = CSVTreeBuilder().build(os.path.join(os.path.dirname(assess_tests.__file__),
                                                   "data/c01-007-102/2/1129-2-process.csv"))
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(signature=signature,
                                                 distance=lambda **kwargs: StartExitDistance(weight=0, **kwargs),
                                                 cache_statistics=SplittedStatistics)
        algorithm.prototypes = [tree]
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in tree.event_iter():
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        self.assertEqual(0, decorator.data()[0][0][0])

    def test_same_attributes_different_count(self):
        tree_1 = Prototype()
        root = tree_1.add_node("root", pid=1, ppid=0, tme=0, exit_tme=0)
        for _ in range(5):
            root.add_node("node", pid=2, ppid=1, tme=0, exit_tme=0)
        tree_2 = Prototype()
        root = tree_2.add_node("root", pid=1, ppid=0, tme=0, exit_tme=0)
        for _ in range(35):
            root.add_node("node", pid=2, ppid=1, tme=0, exit_tme=0)

        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(signature=signature,
                                                 distance=lambda **kwargs: StartExitDistance(weight=0, **kwargs),
                                                 cache_statistics=SplittedStatistics)
        algorithm.prototypes = [tree_1, tree_2]
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in tree_1.event_iter():
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        algorithm.start_tree()
        for event in tree_2.event_iter():
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        data = decorator.data()
        self.assertEqual(data[0][0][1], data[1][0][0])
