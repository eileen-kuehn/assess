from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException
from assess.algorithms.distances.simpledistance import SimpleDistance


class IncrementalDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, distance=SimpleDistance, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._prototype_dict = {}
        self._event_counter = 0
        self._distance = distance()
        self._measured_nodes = set()

    @TreeDistanceAlgorithm.prototypes.setter
    def prototypes(self, value=None):
        for prototype in value:
            # store links to nodes based on node_ids into dictionary
            for process in prototype.nodes():
                signature = self._signature.get_signature(process, process.parent())
                self._prototype_dict.setdefault(signature, set()).add(prototype)
            # initialize default distance to prototypes
            self._distance.init_distance(
                prototypes=self.prototypes,
                prototype_node_count=self.node_count_for_prototype
            )
        TreeDistanceAlgorithm.prototypes.__set__(self, value)

    def start_tree(self):
        self._distance.init_distance(prototypes=self.prototypes, prototype_node_count=self.node_count_for_prototype)
        self._event_counter = 0
        self._measured_nodes = set()
        TreeDistanceAlgorithm.start_tree(self)

    def node_counts(self, original=False):
        if original:
            count = self._tree.node_count()
        else:
            count = len(self._measured_nodes)
        return [count for _ in range(len(self._prototypes))]

    def node_count_for_prototype(self, prototype, original=False):
        if original:
            return prototype.node_count()
        count = 0
        # TODO: maybe work with a filter here
        for values in self._prototype_dict.values():
            for value in values:
                if value == prototype:
                    count += 1
        return count

    def prototypes_converted_for_algorithm(self):
        return self._prototype_dict

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
            matching_prototypes=self._prototype_dict.get(signature, set()),
            prototypes=self.prototypes
        )

    def _finish_node(self, event):
        # just ignoring the exit event of processes here
        pass

    def finish_tree(self):
        return self._distance.finish_distance(prototypes=self._prototypes)

    def _add_traffic(self, event):
        raise NotImplementedError

    def __repr__(self):
        return "%s (%s)" %(self.__class__.__name__, self._distance.__class__.__name__)
