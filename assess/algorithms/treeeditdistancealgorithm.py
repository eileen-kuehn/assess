import zss

from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent


class TreeEditDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._monitoring_results = []
        self._event_counter = 0
        self._supported = {ProcessStartEvent: True}

    def start_tree(self, **kwargs):
        TreeDistanceAlgorithm.start_tree(self, **kwargs)
        self._monitoring_results = []

    def add_events(self, eventgenerator, **kwargs):
        events = list(eventgenerator)
        while len(events) > 1:
            event = events.pop(0)
            if type(event) is ProcessStartEvent:
                TreeDistanceAlgorithm._create_node(self, event)
        self._create_node(events.pop(0))
        return [value for value in self._monitoring_results[-1].values()]

    def _update_distances(self, event, signature, **kwargs):
        prototypes = self._prototypes
        tree = self._tree

        result_dict = dict(zip(self._prototypes, [0] * len(self._prototypes)))
        for prototype in prototypes:
            result_dict[prototype] = self._calculate_distance(prototype.root(), tree.root())

        # add local node distance to global tree distance
        self._add_result_dicts(result_dict)
        return [value for value in self._monitoring_results[-1].values()]

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
