"""
Module offers classes to determine Similarity measures based on start and exit events.
"""

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache


class StartExitSimilarity(Distance):
    """
    The StartExitSimilarity calculates a similarity for dynamic trees based on their start and
    exit events. For exit events statistics like mean and variance are considered.
    """
    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = SignatureCache()

    def init_distance(self):
        Distance.init_distance(self)
        self._signature_cache = SignatureCache()
        for prototype in self._algorithm.prototypes:
            self._monitoring_results_dict[prototype] = 0

    def update_distance(self, signature=None, matching_prototypes=None, value=None, **kwargs):
        self._update_distances(
            prototype_nodes=matching_prototypes,
            node_signature=signature,
            value=value,
        )
        self._signature_cache.add_signature(signature=signature)
        return signature

    def finish_distance(self):
        pass

    def node_count(self):
        return self._signature_cache.frequency()/2.0

    def _update_distances(self, prototype_nodes=None, node_signature=None, value=None):
        prototypes = self._algorithm.prototypes
        result_dict = dict(zip(prototypes, [0] * len(prototypes)))
        for prototype_node in prototype_nodes:
            if self._signature_cache.get(signature=node_signature) < \
                            2*prototype_nodes[prototype_node].count:
                distance = prototype_nodes[prototype_node].distance(value=value)
                if distance is None:
                    result_dict[prototype_node] = 1
                else:
                    result_dict[prototype_node] = 1 - distance
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            result_dict,
            self._monitoring_results_dict
        )
