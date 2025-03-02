import unittest

from assess.algorithms.distances.startexitdistance import StartExitDistance
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.algorithms.signatures.signatures import ParentSiblingSignature, \
    ParentChildByNameTopologySignature
from assess.algorithms.statistics.setstatistics import SetStatistics
from assess.algorithms.statistics.splittedstatistics import SplittedStatistics
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.events.events import TrafficEvent, ProcessStartEvent, ProcessExitEvent, \
    ParameterEvent
from assess.exceptions.exceptions import EventNotSupportedException
from assess.prototypes.simpleprototypes import Tree, Prototype

from assess_tests.basedata import real_tree, simple_prototype, simple_monitoring_tree


class TestStartExitDistance(unittest.TestCase):
    def test_attributes_nodes_only(self):
        def distance(**kwargs):
            distance = StartExitDistance(weight=1, **kwargs)
            distance.supported[TrafficEvent] = True
            return distance
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildByNameTopologySignature(),
            distance=distance,
            cache_statistics=SetStatistics
        )
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)
        algorithm.prototypes = [real_tree("data/c01-007-102/2/1129-2-process.csv")]

        monitoring_tree = real_tree("data/c01-007-102/2/1129-2-process.csv")
        algorithm.start_tree()
        for event in monitoring_tree.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        self.assertEqual([[[0]]], decorator.data())

    def test_external(self):
        def distance(**kwargs):
            distance = StartExitDistance(weight=0, **kwargs)
            distance.supported[TrafficEvent] = True
            return distance
        algorithm = IncrementalDistanceAlgorithm(
            signature=ParentChildByNameTopologySignature(),
            distance=distance,
            cache_statistics=SplittedStatistics)
        decorator = DistanceMatrixDecorator(normalized=False)
        decorator.wrap_algorithm(algorithm)
        the_tree = real_tree(
            path="data/c01-007-102/2/1146-2-process.csv",
            absolute=True
        )
        algorithm.prototypes = [the_tree]
        algorithm.start_tree()
        for event in the_tree.event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        print(decorator.data())
        self.assertTrue(False)

    def test_ensemble(self):
        def distance(**kwargs):
            distance = StartExitDistance(weight=.5, **kwargs)
            distance.supported[TrafficEvent] = False
            return distance
        signature = EnsembleSignature(
            signatures=[
                ParentChildByNameTopologySignature(), ParentSiblingSignature(width=2)])
        algorithm = IncrementalDistanceAlgorithm(
            signature=signature,
            distance=distance,
            cache_statistics=SetStatistics
        )
        decorator = DistanceMatrixDecorator(normalized=True)
        decorator.wrap_algorithm(algorithm)
        algorithm.prototypes = [simple_prototype()]
        algorithm.start_tree()
        for event in simple_monitoring_tree().event_iter(supported=algorithm.supported):
            try:
                algorithm.add_event(event)
            except EventNotSupportedException:
                pass
        algorithm.finish_tree()
        print(decorator.data())
        self.assertTrue(False)

    def test_parameter_distance(self):
        prototype = Prototype()
        root = prototype.add_node("root", tme=0, exit_tme=0, pid=1, ppid=0, param=1)
        for i in range(5):
            root.add_node("child_%d" % i, tme=0, exit_tme=0, pid=i + 2, ppid=1, param=1)
        next(root.children()).add_node("child", tme=0, exit_tme=0, pid=8, ppid=2, param=1)

        tree = Prototype()
        root = tree.add_node("root", tme=0, exit_tme=0, pid=1, ppid=0, param=1)
        for i in range(5):
            root.add_node("child_%d" % i, tme=0, exit_tme=0, pid=i + 2, ppid=1, param=4)
        next(root.children()).add_node("child", tme=0, exit_tme=0, pid=8, ppid=2, param=4)

        for weight, result in [(1, 0), (.5, 6), (0, 12)]:
            def distance(**kwargs):
                distance = StartExitDistance(weight=weight, **kwargs)
                distance.supported = {
                    ProcessStartEvent: True,
                    ProcessExitEvent: True,
                    ParameterEvent: True
                }
                return distance
            signature = EnsembleSignature(signatures=[ParentChildByNameTopologySignature()])
            algorithm = IncrementalDistanceAlgorithm(
                signature=signature,
                distance=distance,
                cache_statistics=SetStatistics
            )
            decorator = DistanceMatrixDecorator(normalized=False)
            decorator.wrap_algorithm(algorithm)
            algorithm.prototypes = [prototype]
            algorithm.start_tree()
            algorithm.add_events(tree.event_iter(supported=algorithm.supported))
            algorithm.finish_tree()
            self.assertEqual(result, decorator.data()[0][0][0])
