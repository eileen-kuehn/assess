import unittest
import os
import assess_tests

from assess.generators.gnm_importer import CSVTreeBuilder, CSVEventStreamer
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.events.events import TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException


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
        for index, event in enumerate(CSVEventStreamer(self.file_path)):
            try:
                distance = alg.add_event(event)
            except EventNotSupportedException:
                pass
        alg.finish_tree()

        self.assertEqual(index + 1, (9109 * 2) + 3155)  # number processes + traffic
        self.assertEqual(distance[0], 0)

    def test_correct_order(self):
        last_tme = 0
        for index, event in enumerate(CSVEventStreamer(self.file_path)):
            self.assertTrue(
                last_tme <= event.tme or (isinstance(event, TrafficEvent) and last_tme <= event.tme + 20),
                "%d: tme of current event should be bigger/equal (%f vs %f)" % (index, last_tme, event.tme)
            )
            last_tme = event.tme
