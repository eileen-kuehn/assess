import os
import unittest

import assess_tests
from assess.algorithms.distances.simpledistance import SimpleDistance
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.algorithms.distances.startexitdistance import StartExitDistance
from assess.algorithms.statistics.setstatistics import SetStatistics
from assess.algorithms.statistics.splittedstatistics import SplittedStatistics
from assess.clustering.clusterdistance import ClusterDistance
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException
from assess.generators.gnm_importer import CSVTreeBuilder
from assess.prototypes.simpleprototypes import Prototype

from assess_tests.basedata import real_tree


class TestComplexExamples(unittest.TestCase):
    def test_attribute_distance(self):
        def distance_buidler(**kwargs):
            distance = StartExitDistance(weight=0, **kwargs)
            distance.supported = {
                ProcessStartEvent: True,
                ProcessExitEvent: True,
                TrafficEvent: True
            }
            return distance

        tree_builder = CSVTreeBuilder()
        tree_1 = tree_builder.build(os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/c01-007-102/2/1129-2-process.csv"))
        tree_2 = tree_builder.build(os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/c01-007-102/2/1136-3-process.csv"))
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature,
            distance=distance_buidler,
            cache_statistics=SplittedStatistics
        )
        algorithm.prototypes = [tree_1, tree_2]
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in tree_1.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        algorithm.start_tree()
        for event in tree_2.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        data = decorator.data()
        print(decorator.data())
        self.assertEqual(4, abs(data[0][0][1] - data[1][0][0]))

    def test_symmetry_optimisation(self):
        tree = CSVTreeBuilder().build(os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/c01-007-102/2/1129-2-process.csv"))
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature,
            distance=lambda **kwargs: StartExitDistance(weight=0, **kwargs),
            cache_statistics=SplittedStatistics)
        algorithm.prototypes = [tree]
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in tree.event_iter(supported=algorithm.supported):
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
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature,
            distance=lambda **kwargs: StartExitDistance(weight=0, **kwargs),
            cache_statistics=SplittedStatistics)
        algorithm.prototypes = [tree_1, tree_2]
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in tree_1.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        algorithm.start_tree()
        for event in tree_2.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        data = decorator.data()
        self.assertEqual(data[0][0][1], data[1][0][0])

    def test_initialisation_of_cluster_representatitives(self):
        def distance_builder(**kwargs):
            distance = StartExitDistance(weight=.5, **kwargs)
            distance.supported[TrafficEvent] = True
            return distance
        tree_one = real_tree()
        tree_two = real_tree(path="data/c01-007-102/2/1129-2-process.csv")
        tree_three = real_tree(path="data/c01-007-102/2/1136-3-process.csv")
        distance = StartExitDistance(weight=.5)
        distance.supported[TrafficEvent] = True
        signature = ParentChildByNameTopologySignature()
        tree_profiles = [tree_one.to_index(
            signature=signature,
            start_support=distance.supported.get(ProcessStartEvent, False),
            exit_support=distance.supported.get(ProcessExitEvent, False),
            traffic_support=distance.supported.get(TrafficEvent, False),
            statistics_cls=SetStatistics
        ), tree_two.to_index(
            signature=signature,
            start_support=distance.supported.get(ProcessStartEvent, False),
            exit_support=distance.supported.get(ProcessExitEvent, False),
            traffic_support=distance.supported.get(TrafficEvent, False),
            statistics_cls=SetStatistics
        ), tree_three.to_index(
            signature=signature,
            start_support=distance.supported.get(ProcessStartEvent, False),
            exit_support=distance.supported.get(ProcessExitEvent, False),
            traffic_support=distance.supported.get(TrafficEvent, False),
            statistics_cls=SetStatistics)
        ]
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildByNameTopologySignature(),
            distance=distance_builder,
            cache_statistics=SetStatistics
        )
        cluster_distance = ClusterDistance(distance=distance)
        prototype_names = ["test"]
        prototype_signatures = []
        for prototype in prototype_names:
            prototype_signatures.append(
                cluster_distance.mean(tree_profiles, prototype=prototype))
        algorithm.cluster_representatives(
            signature_prototypes=prototype_signatures,
            prototypes=prototype_names
        )
        algorithm.start_tree()

    def test_negative_values(self):
        def distance_builder(**kwargs):
            distance = SimpleDistance(**kwargs)
            return distance
        tree_one = real_tree(
            path="data/c01-007-102/2/1078-2-process.csv", absolute=True)
        tree_two = real_tree(
            path="data/c01-007-102/2/1165-2-process.csv", absolute=True)
        signature = ParentChildByNameTopologySignature()
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature,
            distance=distance_builder,
            cache_statistics=SetStatistics
        )
        algorithm.prototypes = [tree_one, tree_two]
        decorator = DistanceMatrixDecorator(normalized=True)
        decorator.wrap_algorithm(algorithm)

        algorithm.start_tree()
        for event in tree_one.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        algorithm.start_tree()
        for event in tree_two.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        print(decorator.data())
        self.assertTrue(False)
