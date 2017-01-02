from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class StartDistance(Distance):
    supported = {ProcessStartEvent: TrafficEvent, ProcessExitEvent: False, TrafficEvent: False}

    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = None

    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        self._signature_cache = [SignatureCache(statistics_cls=signature_prototypes.statistics_cls)
                                 for _ in range(self.signature_count)]
        for prototype in prototypes:
            node_count = prototype.node_count()
            for index in range(self.signature_count):
                self._monitoring_results_dict[index][prototype] = node_count

    def update_distance(self, prototypes, signature_prototypes, event_type=None, matches=[{}],
                        value=None, **kwargs):
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                self._update_distances(
                    prototypes=prototypes,
                    index=index,
                    prototype_nodes=matching_prototypes,
                    node_signature=signature,
                    value=value
                )
                self._signature_cache[index].add_signature(signature=signature)
        return [match.keys() for match in matches]

    def node_count(self, prototypes=None, signature_prototypes=None, signature=False):
        if prototypes is not None:
            return [signature_prototypes.frequency(prototype=prototype) for prototype in prototypes]
        if signature:
            return [signature_cache.node_count() for signature_cache in self._signature_cache]
        return [signature_cache.frequency() for signature_cache in self._signature_cache]

    def _update_distances(self, prototypes, index=0, prototype_nodes=None, node_signature=None,
                          value=None):
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))

        for prototype_node in prototype_nodes:
            # reduce distance as long as the expected node count has not been reached
            if self._signature_cache[index].get_count(signature=node_signature) < \
                            prototype_nodes[prototype_node]["duration"].count():
                result_dict[prototype_node] = -1
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )
