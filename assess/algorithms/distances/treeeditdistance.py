"""
Wrapper Distance object for TreeEditDistance
"""
import zss

from assess.algorithms.distances.distance import Distance
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class TreeEditDistance(Distance):
    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._tree = None
        self._signature = None
        self._based_on_original = True

    def init_distance(self, tree, signature, **kwargs):
        Distance.init_distance(self, **kwargs)
        self.supported = {ProcessStartEvent: True, ProcessExitEvent: False, TrafficEvent: False}
        self._tree = tree
        self._signature = signature

    def node_count(self, prototypes=None, **kwargs):
        if prototypes is not None:
            # FIXME: dirty hack
            return [[prototype.node_count() for prototype in prototypes]]
        return self._tree.node_count()

    def update_distance(self, prototypes, signature_prototypes, event_type=None, matches=[{}],
                        **kwargs):
        # don't do anything here
        pass

    def finish_distance(self, prototypes, signature_prototypes):
        tree = self._tree

        result_dict = dict(zip(prototypes, [0 for _ in range(len(prototypes))]))
        for prototype in prototypes:
            result_dict[prototype] = self._calculate_distance(prototype.root(), tree.root())

        # add local node distance to global tree distance
        # taking index 0 here, because usually, TED is not used in an ensemble
        self._monitoring_results_dict[0] = result_dict

    def _calculate_distance(self, prototype, tree):
        return zss.simple_distance(
            prototype,
            tree,
            lambda node: list(node.children()),
            lambda node: self._signature.get_signature(node, node.parent()),
            lambda prototype_label, tree_label: prototype_label != tree_label
        )
