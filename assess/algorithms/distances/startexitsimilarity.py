"""
Module offers classes to determine Similarity measures based on start and exit events.
"""

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache
from assess.events.events import ProcessExitEvent, ProcessStartEvent


class StartExitSimilarity(Distance):
    """
    The StartExitSimilarity calculates a similarity for dynamic trees based on
    their start and exit events. For exit events statistics like mean and variance
    are considered.
    """
    __slots__ = "_signature_cache"

    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = None

    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        self._signature_cache = [SignatureCache(
            statistics_cls=signature_prototypes.statistics_cls,
            supported=self.supported
        ) for _ in range(len(self._monitoring_results_dict))]
        for prototype in prototypes:
            for index in range(self.signature_count):
                self._monitoring_results_dict[index][prototype] = 0

    def update_distance(self, prototypes, signature_prototypes, event_type=None,
                        matches=None, value=None, **kwargs):
        if matches is None:
            matches = []
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                if signature is None:
                    continue
                self._update_distances(
                    prototypes=prototypes,
                    index=index,
                    prototype_nodes=matching_prototypes,
                    node_signature=signature,
                    value=value,
                    event_type=event_type
                )
                if event_type == ProcessStartEvent:
                    self._signature_cache[index][signature, event_type] = {
                        "value": 0
                    }
                else:
                    self._signature_cache[index][signature, event_type] = {
                        "value": value
                    }
        return [list(match)[0] for match in matches]

    def node_count(self, prototypes=None, signature_prototypes=None, signature=False,
                   by_event=False):
        if prototypes is not None:
            return [signature_prototypes.frequency(
                prototype=prototype
            ) for prototype in prototypes]
        if signature:
            return [signature_cache.node_count() for signature_cache in
                    self._signature_cache]
        return [signature_cache.frequency() for signature_cache in
                self._signature_cache]

    def _update_distances(self, prototypes, index=0, prototype_nodes=None,
                          node_signature=None, value=None, event_type=None):
        result_dict = dict.fromkeys(prototypes, 0)
        for prototype_node in prototype_nodes:
            # FIXME: Ich denke die 2* muss entfernt werden
            statistic = prototype_nodes[prototype_node][ProcessExitEvent]["value"]
            if self._signature_cache[index].multiplicity(
                    signature=node_signature,
                    event_type=ProcessExitEvent
            ) < 2 * statistic.count():
                distance = statistic.distance(value=value)
                if distance is None:
                    result_dict[prototype_node] = 1
                else:
                    result_dict[prototype_node] = 1 - distance
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )
