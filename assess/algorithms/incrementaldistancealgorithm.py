from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException


class IncrementalDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._prototype_dict = {}
        self._monitoring_results_dict = {}
        self._event_counter = 0

        self._measured_nodes = set()

    @TreeDistanceAlgorithm.prototypes.setter
    def prototypes(self, value=None):
        for prototype in value:
            # store links to nodes based on node_ids into dictionary
            for process in prototype.nodes():
                signature = self._signature.get_signature(process, process.parent())
                self._prototype_dict.setdefault(signature, set()).add(prototype)
            # initialize default distance to prototypes
            self._init_default_distances()
        TreeDistanceAlgorithm.prototypes.__set__(self, value)

    def _init_default_distances(self):
        self._monitoring_results_dict = {}
        for prototype in self.prototypes:
            self._monitoring_results_dict[prototype] = self.node_count_for_prototype(prototype, original=False)

    def start_tree(self):
        self._init_default_distances()
        self._event_counter = 0
        self._measured_nodes = set()
        TreeDistanceAlgorithm.start_tree(self)

    def node_counts(self, original=False):
        if original:
            count = self._tree.node_count()
        else:
            count = len(self._measured_nodes)
        return [count for i in range(len(self._prototypes))]

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
        return [value for value in self._monitoring_results_dict.values()]

    def _create_node(self, event, **kwargs):
        signature = TreeDistanceAlgorithm._create_node(self, event, **kwargs)
        # print(self._prototypes[0].tree_repr(node_repr=lambda thenode: thenode.signature_id[self._signature]))
        # print(self._monitoring_tree.tree_repr(node_repr=lambda thenode: thenode.signature_id[self._signature]))
        if signature not in self._measured_nodes:
            self._update_distances(
                    self._prototype_dict.get(signature, set()),
                    signature)
            self._measured_nodes.add(signature)
        return signature

    def _finish_node(self, event):
        # just ignoring the exit event of processes here
        pass

    def _add_traffic(self, event):
        raise NotImplementedError

    def _update_distances(self, prototype_nodes, node_signature):
        result_dict = dict(zip(self._prototypes, [1] * len(self._prototypes)))
        for prototype_node in prototype_nodes:
            result_dict[prototype_node] = -1
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)

    def _add_result_dicts(self, first, second):
        result = dict((key, first[key] + second[key]) for key in set(first.keys() + second.keys()))
        return result
