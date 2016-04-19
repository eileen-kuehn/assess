import zss

from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent
from assess.exceptions.exceptions import EventNotSupportedException


class TreeEditDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._monitoring_results = []
        self._event_counter = 0

    def start_tree(self, **kwargs):
        TreeDistanceAlgorithm.start_tree(self, **kwargs)
        self._monitoring_results = []
        self._event_counter = 0

    def add_events(self, eventgenerator, **kwargs):
        events = list(eventgenerator)
        while len(events) > 1:
            event = events.pop(0)
            if type(event) is ProcessStartEvent:
                TreeDistanceAlgorithm._create_node(self, event)
        self._create_node(events.pop(0))
        return [value for value in self._monitoring_results[-1].values()]

    def _add_event(self, event, **kwargs):
        # just adding, but not removing nodes
        self._event_counter += 1
        if type(event) is ProcessStartEvent:
            self._create_node(event)
        elif type(event) is ProcessExitEvent:
            pass
        else:
            raise EventNotSupportedException(event)
        return [value for value in self._monitoring_results[-1].values()]

    def _create_node(self, event):
        signature = TreeDistanceAlgorithm._create_node(self, event)
        self._update_distances(self._prototypes, self._tree)
        return signature

    def _update_distances(self, prototypes, tree):
        result_dict = dict(zip(self._prototypes, [0] * len(self._prototypes)))

        for prototype in prototypes:
            result_dict[prototype] = self._calculate_distance(prototype.root(), tree.root())

        # add local node distance to global tree distance
        self._add_result_dicts(result_dict)

    def _calculate_distance(self, prototype, tree):
        return zss.simple_distance(
                prototype,
                tree,
                lambda node: list(node.children()),
                lambda node: self._signature.get_signature(node, node.parent()),
                lambda prototype_label, tree_label: prototype_label != tree_label
        )

    def _add_result_dicts(self, results):
        return self._monitoring_results.append(results)
