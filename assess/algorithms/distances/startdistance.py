from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class StartDistance(Distance):
    __slots__ = "_signature_cache"

    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = None
        self.supported = {
            ProcessStartEvent: True,
            ProcessExitEvent: False,
            TrafficEvent: False
        }

    def init_distance(self, prototypes, signature_prototypes):
        super().init_distance(prototypes, signature_prototypes)
        self._signature_cache = [SignatureCache(
            statistics_cls=signature_prototypes.statistics_cls,
            supported=self.supported
        ) for _ in range(self.signature_count)]
        for prototype in prototypes:
            for index in range(self.signature_count):
                node_count = signature_prototypes.multiplicity(prototype=prototype)
                try:
                    self._monitoring_results_dict[index][prototype] = node_count[index]
                except TypeError:
                    self._monitoring_results_dict[index][prototype] = node_count

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
                    value=value
                )
                self._signature_cache[index][signature, event_type] = {"value": value}
        return [match.keys() for match in matches]

    def node_count(self, prototypes=None, signature_prototypes=None, signature=False,
                   by_event=False):
        if prototypes is not None:
            return [signature_prototypes.multiplicity(
                prototype=prototype,
                by_event=by_event
            ) for prototype in prototypes]
        if signature:
            return [signature_cache.node_count() for signature_cache in
                    self._signature_cache]
        return [signature_cache.multiplicity() for signature_cache in
                self._signature_cache]

    def event_count(self, by_event=False):
        return [signature_cache.multiplicity(by_event=by_event) for signature_cache in
                self._signature_cache]

    def _update_distances(self, prototypes, index=0, prototype_nodes=None,
                          node_signature=None, value=None):
        result_dict = dict.fromkeys(prototypes, 1)

        for prototype_node in prototype_nodes:
            # reduce distance as long as the expected node count has not been reached
            if self._signature_cache[index].multiplicity(
                    signature=node_signature,
                    event_type=ProcessStartEvent
            ) < prototype_nodes[prototype_node][ProcessStartEvent]["value"].count():
                result_dict[prototype_node] = -1
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )
