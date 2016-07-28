"""
Module offers functionality to execute an incremental distance measurement for dynamic trees.
"""

from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.algorithms.distances.simpledistance import SimpleDistance
from assess.algorithms.signatures.signatures import Signature
from assess.events.events import ProcessStartEvent, ProcessExitEvent


class IncrementalDistanceAlgorithm(TreeDistanceAlgorithm):
    """
    The IncrementalDistanceAlgorithm takes care to adapt distance calculation for dynamic trees.
    """
    def __init__(self, signature=Signature(), distance=SimpleDistance, **kwargs):
        TreeDistanceAlgorithm.__init__(self, signature, **kwargs)
        self._distance = None
        self._measured_nodes = set()  # TODO: can those be removed?
        self._distance_builder = distance
        self._supported = {ProcessStartEvent: True, ProcessExitEvent: True}

    @property
    def distance(self):
        """
        Property to retrieve the currently used distance method.

        :return: Distance in use
        """
        if self._distance is None:
            self._distance = self._distance_builder(algorithm=self)
        return self._distance

    @TreeDistanceAlgorithm.prototypes.setter
    def prototypes(self, value=None):
        self.distance.init_distance()
        TreeDistanceAlgorithm.prototypes.__set__(self, value)

    def start_tree(self, **kwargs):
        TreeDistanceAlgorithm.start_tree(self, **kwargs)
        self.distance.init_distance()
        self._measured_nodes = set()

    def _prototype_event_counts(self):
        if self.distance.is_prototype_based_on_original():
            return [prototype.node_count() for prototype in self._prototypes]
        return [self._signature_prototypes.node_count(prototype=prototype) for
                prototype in self._prototypes]

    def _event_count(self):
        return self.distance.node_count()

    def _update_distances(self, event, signature, **kwargs):
        try:
            self.distance.update_distance(
                signature=signature,
                value=float(event.tme)-float(event.start_tme),
                matching_prototypes=self._signature_prototypes.get(signature=signature)
            )
        except AttributeError:
            self.distance.update_distance(
                signature=signature,
                matching_prototypes=self._signature_prototypes.get(signature=signature)
            )
        return [value for value in self.distance]

    def finish_tree(self):
        return self.distance.finish_distance()

    def __repr__(self):
        return "%s (%s)" %(self.__class__.__name__, self.distance.__class__.__name__)
