"""
Module offers functionality to perform the well-known tree edit distance based on the current
framework for dynamic trees.
"""
from assess.algorithms.distances.treeeditdistance import TreeEditDistance
from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm


class TreeEditDistanceAlgorithm(TreeDistanceAlgorithm):
    """
    Implementation of tree edit distance based on dynamic trees by waiting until the whole tree
    is generated. The algorithm itself is just based on process start events and ignores actual
    exit events.
    """
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._distance = TreeEditDistance()

    @property
    def distance(self):
        """
        Property to retrieve the currently used distance method.

        :return: Distance in use
        """
        return self._distance

    def start_tree(self, **kwargs):
        TreeDistanceAlgorithm.start_tree(self, **kwargs)
        self.distance.init_distance(prototypes=self.prototypes,
                                    signature_prototypes=self.signature_prototypes,
                                    tree=self._tree,
                                    signature=self._signature)
        self.supported = self.distance.supported

    def finish_tree(self):
        self.distance.finish_distance(self.prototypes, self.signature_prototypes)
        result = [value for value in self.distance.iter_on_prototypes(self._prototypes)]
        return [list(element) for element in zip(*result)]

    def _update_distances(self, event, signature, **kwargs):
        self.distance.update_distance(prototypes=self._prototypes, signature_prototypes=None, )
        result = [value for value in self.distance.iter_on_prototypes(self._prototypes)]
        return [list(element) for element in zip(*result)]
