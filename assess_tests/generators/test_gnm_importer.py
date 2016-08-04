import unittest
import os
import assess_tests
import random

from assess.generators.gnm_importer import CSVTreeBuilder, GNMCSVEventStreamer, \
    EventStreamer, EventStreamPruner, EventStreamBranchPruner, EventStreamRelabeler, \
    EventStreamBranchRelabeler
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException
from assess.algorithms.signatures.signatures import *


class TestGNMImporter(unittest.TestCase):
    def setUp(self):
        self.file_path = os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/c01-007-102/1/1-process.csv"
        )
        self.old_file_path = os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/gnm-process.csv"
        )

    def test_csv_tree(self):
        tree_builder = CSVTreeBuilder()
        tree = tree_builder.build(self.old_file_path)
        self.assertIsNotNone(tree)
        self.assertEqual(tree.node_count(), 21800)

    def test_csv_stream(self):
        tree_builder = CSVTreeBuilder()
        alg = IncrementalDistanceAlgorithm()
        alg.prototypes = [tree_builder.build(self.file_path)]
        alg.start_tree()
        for index, event in enumerate(EventStreamer(streamer=GNMCSVEventStreamer(self.file_path))):
            try:
                distance = alg.add_event(event)
            except EventNotSupportedException:
                pass
        alg.finish_tree()

        self.assertEqual(index + 1, (9109 * 2) + 3155)  # number processes + traffic
        self.assertEqual(distance[0], 0)

    def test_correct_order(self):
        last_tme = 0
        for index, event in enumerate(EventStreamer(streamer=GNMCSVEventStreamer(self.file_path))):
            self.assertTrue(
                last_tme <= event.tme or (isinstance(event, TrafficEvent) and last_tme <= event.tme + 20),
                "%d: tme of current event should be bigger/equal (%f vs %f)" % (index, last_tme, event.tme)
            )
            last_tme = event.tme

    def test_gnm_csv_event_streamer(self):
        # FIXME: I would expect also traffic to be streamed here...
        last_tme = 0
        for index, event in enumerate(GNMCSVEventStreamer(csv_path=self.file_path)):
            self.assertTrue(last_tme <= event.tme)
            last_tme = event.tme

    def test_gnm_event_streamer(self):
        csv_event_streamer = GNMCSVEventStreamer(csv_path=self.file_path)
        last_tme = 0
        for index, event in enumerate(EventStreamer(streamer=csv_event_streamer)):
            self.assertTrue(
                last_tme <= event.tme or (isinstance(event, TrafficEvent) and last_tme <= event.tme + 20),
                "%d: tme of current event should be bigger/equal (%f vs %f)" % (index, last_tme, event.tme)
            )
            last_tme = event.tme

    def test_event_stream_pruner(self):
        random.seed(815)
        csv_event_streamer = GNMCSVEventStreamer(csv_path=self.file_path)
        node_stream_pruner = EventStreamPruner(
            signature=ParentChildByNameTopologySignature(),
            chance=.1,
            streamer=csv_event_streamer)
        last_tme = 0
        for index, event in enumerate(EventStreamer(streamer=node_stream_pruner)._streamer.node_iter()):
            self.assertTrue(
                last_tme <= event.tme or (isinstance(event, TrafficEvent) and last_tme <= event.tme + 20),
                "%d: tme of current event should be bigger/equal (%f vs %f)" % (index, last_tme, event.tme)
            )
            last_tme = event.tme

    def test_event_stream_branch_pruner(self):
        random.seed(815)
        csv_event_streamer = GNMCSVEventStreamer(csv_path=self.file_path)
        node_stream_branch_pruner = EventStreamBranchPruner(
            signature=ParentChildByNameTopologySignature(),
            chance=.1,
            streamer=csv_event_streamer
        )
        last_tme = 0
        for index, event in enumerate(EventStreamer(streamer=node_stream_branch_pruner)._streamer.node_iter()):
            self.assertTrue(
                last_tme <= event.tme or (isinstance(event, TrafficEvent) and last_tme <= event.tme + 20),
                "%d: tme of current event should be bigger/equal (%f vs %f)" % (index, last_tme, event.tme)
            )
            last_tme = event.tme

    def test_event_stream_relabeler(self):
        random.seed(815)
        chance = .1
        csv_event_streamer = GNMCSVEventStreamer(csv_path=self.file_path)
        event_stream_relabeler = EventStreamRelabeler(
            signature=ParentChildByNameTopologySignature(),
            chance=chance,
            streamer=csv_event_streamer
        )
        count = 0
        traffic_events = 0
        for index, event in enumerate(EventStreamer(streamer=event_stream_relabeler)._streamer.node_iter()):
            try:
                if "_relabel" in event.name:
                    count += 1
            except AttributeError:
                traffic_events += 1
        self.assertEqual(757, count)
        self.assertAlmostEqual(chance, count / float(index - traffic_events), 1)

    def test_event_stream_branch_relabeler(self):
        random.seed(815)
        chance = .1
        csv_event_streamer = GNMCSVEventStreamer(csv_path=self.file_path)
        event_stream_relabeler = EventStreamBranchRelabeler(
            signature=ParentChildByNameTopologySignature(),
            chance=chance,
            streamer=csv_event_streamer
        )
        count = 0
        traffic_events = 0
        for index, event in enumerate(EventStreamer(streamer=event_stream_relabeler)._streamer.node_iter()):
            try:
                if "_relabel" in event.name:
                    count += 1
            except AttributeError:
                traffic_events += 1
        self.assertEqual(4608, count)
        self.assertAlmostEqual(chance*5, count / float(index - traffic_events), 1)

    def test_correct_ppids(self):
        # TODO: implement me (when removing nodes from tree, ppids need to be set)
        csv_event_streamer = GNMCSVEventStreamer(csv_path=self.file_path)
        node_stream_pruner = EventStreamPruner(
            signature=ParentChildByNameTopologySignature(),
            chance=.5,
            streamer=csv_event_streamer
        )
        for node in EventStreamer(streamer=node_stream_pruner)._streamer.node_iter():
            parent = node.parent()
            if parent is not None:
                self.assertEqual(node.ppid, parent.pid)
