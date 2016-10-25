from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache
from assess.events.events import ProcessExitEvent


class StartDistance(Distance):
    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = None

    def init_distance(self):
        Distance.init_distance(self)
        self._algorithm.supported[ProcessExitEvent] = False
        self._signature_cache = [SignatureCache() for _ in range(self._algorithm.signature.count)]
        for prototype in self._algorithm.prototypes:
            node_count = prototype.node_count()
            for index in range(self._algorithm.signature.count):
                self._monitoring_results_dict[index][prototype] = node_count

    def update_distance(self, matches=[{}], value=None, **kwargs):
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                self._update_distances(
                    index=index,
                    prototype_nodes=matching_prototypes,
                    node_signature=signature,
                    value=value
                )
                self._signature_cache[index].add_signature(signature=signature)
        return [match.keys() for match in matches]

    def finish_distance(self):
        pass

    def node_count(self):
        return [signature_cache.frequency() for signature_cache in self._signature_cache]

    def _update_distances(self, index=0, prototype_nodes=None, node_signature=None, value=None):
        prototypes = self._algorithm.prototypes
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))

        for prototype_node in prototype_nodes:
            # reduce distance as long as the expected node count has not been reached
            if self._signature_cache[index].get(signature=node_signature) < \
                            prototype_nodes[prototype_node].count:
                result_dict[prototype_node] = -1
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )
