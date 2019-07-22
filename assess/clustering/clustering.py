import dengraph.graph
from dengraph.dengraph import DenGraphIO
from dengraph.graphs.adjacency_graph import AdjacencyGraph
from dengraph.graphs.distance_graph import DistanceGraph

from assess.clustering.clusterdistance import ClusterDistance


class Clustering(object):
    def __init__(self, distance, cluster_distance=.1, core_neighbours=5):
        self._nodes = []
        self._clusterer = None
        self.distance = distance
        self.cluster_distance = cluster_distance
        self.core_neighbours = core_neighbours

    @property
    def clusterer(self):
        if self._clusterer is None:
            distance = ClusterDistance(distance=self.distance)
            self._clusterer = DenGraphIO(
                base_graph=AdjacencyGraph(DistanceGraph(
                    nodes=self._nodes,
                    distance=distance,
                    symmetric=True
                )),
                cluster_distance=self.cluster_distance,
                core_neighbours=self.core_neighbours
            )
            self._clusterer.graph.distance = distance
        return self._clusterer

    def __setitem__(self, key, value):
        """
        Adding a new sketch from a finished dynamic tree to the underlying
        clustering algorithm. The actual sketch is contained in key. Value is
        not specified so far.

        :param key:
        :param value:
        :return:
        """
        value.key = key
        self._nodes.append(value)

    def __getitem__(self, item):
        """
        This method returns the belonging cluster for a given sketch that is
        contained in the underlying clustering algorithm.

        :param item:
        :return:
        """
        if item in self.clusterer.graph:
            return self.clusterer.clusters_for_node(item)
        # TODO: here a more general exception might be raised to make
        # algorithm exchangeable
        raise dengraph.graph.NoSuchNode

    def __iter__(self):
        """
        Iterates over the determined clusters from underlying clustering algorithm.

        :return:
        """
        for cluster in self.clusterer:
            yield cluster
