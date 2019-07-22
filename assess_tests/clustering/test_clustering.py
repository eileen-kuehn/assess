import os
import unittest

import assess_tests

from assess.clustering.clustering import Clustering
from assess.generators.gnm_importer import CSVTreeBuilder
from assess.algorithms.signatures.signatures import ParentChildByNameTopologySignature
from assess.algorithms.distances.startexitdistance import StartExitDistance


class TestClustering(unittest.TestCase):
    def setUp(self):
        self.file_path_one = os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/c01-007-102/1/1-process.csv"
        )
        self.file_path_two = os.path.join(
            os.path.dirname(assess_tests.__file__),
            "data/c01-007-102/2/83721-5-process.csv"
        )

    def test_simple_clustering(self):
        clusterer = Clustering(distance=StartExitDistance())
        # create an index to cluster
        builder = CSVTreeBuilder()
        tree = builder.build(self.file_path_one)
        tree_two = builder.build(self.file_path_two)
        tree_index = tree.to_index(signature=ParentChildByNameTopologySignature())
        tree_two_index = tree_two.to_index(
            signature=ParentChildByNameTopologySignature())
        clusterer[1] = tree_index
        clusterer[1] = tree_two_index
        self.assertEqual(0, len(clusterer.clusterer.clusters))
        self.assertEqual(2, len(clusterer.clusterer.noise))
