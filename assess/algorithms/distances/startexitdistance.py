from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache


class StartExitDistance(Distance):
    """
    TODO: write description
    """
    def __init__(self):
        Distance.__init__(self)
        self._based_on_original = True
        self._signature_cache = SignatureCache()

    def init_distance(self, prototypes=None, signature_prototypes=None):
        Distance.init_distance(self, prototypes=prototypes, signature_prototypes=signature_prototypes)
        self._signature_cache = SignatureCache()
        for prototype in prototypes:
            self._monitoring_results_dict[prototype] = prototype.node_count()

    def update_distance(self, signature=None, matching_prototypes=None, prototypes=None, value=None,
                        signature_prototypes=None, **kwargs):
        self._update_distances(
                prototype_nodes=matching_prototypes,
                node_signature=signature,
                prototypes=prototypes,
                value=value,
                signature_prototypes=signature_prototypes
        )
        self._signature_cache.add_signature(signature=signature)
        return signature

    def finish_distance(self, prototypes=None, signature_prototypes=None):
        pass

    def node_count(self):
        return self._signature_cache.frequency()/2.0

    def _update_distances(self, prototype_nodes=None, node_signature=None, prototypes=None, value=None, signature_prototypes=None):
        result_dict = dict(zip(prototypes, [.5] * len(prototypes)))
        for prototype_node in prototype_nodes:
            if self._signature_cache.get(signature=node_signature) < 2*prototype_nodes[prototype_node].count:
                distance = prototype_nodes[prototype_node].distance(value=value)
                if distance is None:
                    result_dict[prototype_node] = -.5
                elif distance > .5:
                    result_dict[prototype_node] = .5 - distance
                else:
                    result_dict[prototype_node] = distance
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)
