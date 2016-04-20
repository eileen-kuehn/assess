from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException
from assess.algorithms.distances.simpledistance import SimpleDistance


class IncrementalDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, distance=SimpleDistance, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._event_counter = 0
        self._distance = None
        self._measured_nodes = set()
        self._distance_builder = distance

    @TreeDistanceAlgorithm.prototypes.setter
    def prototypes(self, value=None):
        # initialize default distance to prototypes
        if self._distance is None:
            self._distance = self._distance_builder(prototypes=value)
        self._distance.init_distance(
            prototypes=self.prototypes,
            signature_prototypes=self.signature_prototypes
        )
        TreeDistanceAlgorithm.prototypes.__set__(self, value)

    def start_tree(self, **kwargs):
        TreeDistanceAlgorithm.start_tree(self, **kwargs)
        self._distance.init_distance(prototypes=self.prototypes, signature_prototypes=self.signature_prototypes)
        self._event_counter = 0
        self._measured_nodes = set()

    def _prototype_event_counts(self):
        if self._distance.is_prototype_based_on_original():
            return [prototype.node_count() for prototype in self._prototypes]
        return [self._signature_prototypes.node_count(prototype=prototype) for prototype in self._prototypes]

    def _event_count(self):
        return self._distance.node_count()

    def _add_event(self, event, **kwargs):
        self._event_counter += 1
        if type(event) is ProcessStartEvent:
            self._create_node(event)
        elif type(event) is ProcessExitEvent:
            self._finish_node(event)
        elif type(event) is TrafficEvent:
            self._add_traffic(event)
        else:
            raise EventNotSupportedException(event)
        return [value for value in self._distance]

    def _create_node(self, event, **kwargs):
        signature = TreeDistanceAlgorithm._create_node(self, event, **kwargs)
        # print(self._prototypes[0].tree_repr(node_repr=lambda thenode: thenode.signature_id[self._signature]))
        # print(self._monitoring_tree.tree_repr(node_repr=lambda thenode: thenode.signature_id[self._signature]))
        return self._distance.update_distance(
            signature=signature,
            matching_prototypes=self._signature_prototypes.get(signature=signature),
            prototypes=self.prototypes,
            signature_prototypes=self.signature_prototypes
        )

    def _finish_node(self, event, **kwargs):
        signature = TreeDistanceAlgorithm._finish_node(self, event, **kwargs)
        return self._distance.update_distance(
            signature=signature,
            value=float(event.tme)-float(event.start_tme),
            matching_prototypes=self._signature_prototypes.get(signature=signature),
            prototypes=self.prototypes,
            signature_prototypes=self.signature_prototypes
        )

    def finish_tree(self):
        return self._distance.finish_distance(prototypes=self._prototypes, signature_prototypes=self.signature_prototypes)

    def __repr__(self):
        return "%s (%s)" %(self.__class__.__name__, self._distance.__class__.__name__)
