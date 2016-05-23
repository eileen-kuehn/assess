import unittest
import os
import assess_tests

from assess.generators.gnm_importer import CSVTreeBuilder, CSVEventStreamer
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm


class TestGNMImporter(unittest.TestCase):
    def setUp(self):
        self.file_path = os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/gnm-process.csv"
        )

    def test_csv_tree(self):
        tree_builder = CSVTreeBuilder()
        tree = tree_builder.build(self.file_path)
        self.assertIsNotNone(tree)
        self.assertEqual(tree.node_count(), 21800)

    def test_csv_stream(self):
        tree_builder = CSVTreeBuilder()
        alg = IncrementalDistanceAlgorithm()
        alg.prototypes = [tree_builder.build(self.file_path)]
        alg.start_tree()
        for index, event in enumerate(CSVEventStreamer(self.file_path)):
            distance = alg.add_event(event)
        alg.finish_tree()

        self.assertEqual(index, (21800 * 2) - 1)
        self.assertEqual(distance[0], 0)
