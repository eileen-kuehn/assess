"""
Module offers functionality to execute an incremental distance measurement for dynamic trees.
"""

from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.algorithms.distances.simpledistance import SimpleDistance
from assess.algorithms.signatures.signatures import Signature
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class IncrementalDistanceAlgorithm(TreeDistanceAlgorithm):
    """
    The IncrementalDistanceAlgorithm takes care to adapt distance calculation for dynamic trees.
    """
    def __init__(self, signature=Signature(), distance=SimpleDistance, cache_statistics=None, **kwargs):
        TreeDistanceAlgorithm.__init__(self, signature=signature,
                                       cache_statistics=cache_statistics, **kwargs)
        self._distance = None
        self._measured_nodes = set()  # TODO: can those be removed?
        self._distance_builder = distance
        self.supported = {ProcessStartEvent: True, ProcessExitEvent: True, TrafficEvent: False}

    @property
    def distance(self):
        """
        Property to retrieve the currently used distance method.

        :return: Distance in use
        """
        if self._distance is None:
            self._distance = self._distance_builder(signature_count=self.signature.count)
        return self._distance

    @TreeDistanceAlgorithm.prototypes.setter
    def prototypes(self, value=None):
        self.distance.init_distance(prototypes=self.prototypes,
                                    signature_prototypes=self.signature_prototypes)
        TreeDistanceAlgorithm.prototypes.__set__(self, value)

    def start_tree(self, **kwargs):
        TreeDistanceAlgorithm.start_tree(self, **kwargs)
        self.distance.init_distance(prototypes=self.prototypes,
                                    signature_prototypes=self.signature_prototypes)
        self.supported = self.distance.supported
        self._measured_nodes = set()

    def _prototype_event_counts(self):
        if self.distance.is_prototype_based_on_original():
            return [[prototype.node_count() for prototype in self._prototypes] for _ in range(
                self._signature.count)]
        result = [self._signature_prototypes.node_count(prototype=prototype)
                  for prototype in self._prototypes]
        return [[element[i] for element in result] for i in range(len(result[0]))]

    def _event_count(self):
        return [[count for _ in self.prototypes] for count in self.distance.node_count()]

    def _update_distances(self, event, signature, **kwargs):
        matching_prototypes = self._signature_prototypes.get(signature=signature)
        try:
            self.distance.update_distance(
                prototypes=self.prototypes,
                signature_prototypes=self.signature_prototypes,
                event_type=type(event),
                matches=[{token: matching_prototypes[index]}
                         for index, token in enumerate(signature)],
                value=float(event.tme)-float(event.start_tme),
            )
        except AttributeError:
            self.distance.update_distance(
                prototypes=self.prototypes,
                signature_prototypes=self.signature_prototypes,
                event_type=type(event),
                matches=[{token: matching_prototypes[index]}
                         for index, token in enumerate(signature)]
            )
        # [[p1e1, ..., p1en], ..., [pne1, ..., pnen]]
        result = [value for value in self.distance.iter_on_prototypes(self.prototypes)]
        return [list(element) for element in zip(*result)]

    def finish_tree(self):
        return self.distance.finish_distance(self.prototypes, self.signature_prototypes)

    def __repr__(self):
        return "%s (%s)" %(self.__class__.__name__, self.distance.__class__.__name__)
