from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException


class IncrementalDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._prototype_dict = {}
        self._monitoring_results_dict = {}
        self._event_counter = 0

    @TreeDistanceAlgorithm.prototypes.setter
    def prototypes(self, value=None):
        for prototype in value:
            # store links to nodes based on node_ids into dictionary
            for process in prototype.nodes():
                self._prototype_dict.setdefault(self._signature.get_signature(process), []).append(process)
            # initialize default distance to prototypes
            self._monitoring_results_dict[prototype] = 0
        TreeDistanceAlgorithm.prototypes.__set__(self, value)

    def node_counts(self):
        return [self._tree.node_count() for prototype in self._prototypes]

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
        return [value for value in self._monitoring_results_dict.values()]

    def _create_node(self, event, **kwargs):
        node = TreeDistanceAlgorithm._create_node(self, event, **kwargs)
        # print(self._prototypes[0].tree_repr(node_repr=lambda thenode: thenode.signature_id[self._signature]))
        # print(self._monitoring_tree.tree_repr(node_repr=lambda thenode: thenode.signature_id[self._signature]))
        node_signature = self._signature.get_signature(node)
        self._update_distances(
                self._prototype_dict.get(node_signature, []),
                node_signature)
        return node

    def _finish_node(self, event):
        # just ignoring the exit event of processes here
        pass

    def _add_traffic(self, event):
        raise NotImplementedError

    def _update_distances(self, prototype_nodes, node_signature):
        result_dict = dict(zip(self._prototypes, [1] * len(self._prototypes)))
        for prototype_node in prototype_nodes:
            result_dict[prototype_node._prototype] = 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)

    def _add_result_dicts(self, first, second):
        result = dict((key, first[key] + second[key]) for key in set(first.keys() + second.keys()))
        return result
