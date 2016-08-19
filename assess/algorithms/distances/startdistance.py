from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache
from assess.events.events import ProcessExitEvent


class StartDistance(Distance):
    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = SignatureCache()

    def init_distance(self):
        Distance.init_distance(self)
        self._algorithm.supported[ProcessExitEvent] = False
        self._signature_cache = SignatureCache()
        for prototype in self._algorithm.prototypes:
            self._monitoring_results_dict[prototype] = prototype.node_count()

    def update_distance(self, signature=None, matching_prototypes=None, value=None, **kwargs):
        self._update_distances(
            prototype_nodes=matching_prototypes,
            node_signature=signature,
            value=value
        )
        self._signature_cache.add_signature(signature=signature)
        return signature

    def finish_distance(self):
        pass

    def node_count(self):
        return self._signature_cache.frequency()

    def _update_distances(self, prototype_nodes=None, node_signature=None, value=None):
        prototypes = self._algorithm.prototypes
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))
        for prototype_node in prototype_nodes:
            # reduce distance as long as the expected node count has not been reached
            if self._signature_cache.get(signature=node_signature) < \
                            prototype_nodes[prototype_node].count:
                result_dict[prototype_node] = -1
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            result_dict,
            self._monitoring_results_dict
        )
