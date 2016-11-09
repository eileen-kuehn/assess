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
        self._signature_cache = None

    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        self._signature_cache = [SignatureCache() for _ in range(len(self._monitoring_results_dict))]
        for prototype in prototypes:
            for index in range(self.signature_count):
                self._monitoring_results_dict[index][prototype] = 0

    def update_distance(self, prototypes, signature_prototypes, event_type=None, matches=[{}], value=None, **kwargs):
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                self._update_distances(
                    prototypes=prototypes,
                    index=index,
                    prototype_nodes=matching_prototypes,
                    node_signature=signature,
                    value=value,
                )
                self._signature_cache[index].add_signature(signature=signature)
        return [match.keys()[0] for match in matches]

    def node_count(self):
        return [signature_cache.frequency()/2.0 for signature_cache in self._signature_cache]

    def _update_distances(self, prototypes, index=0, prototype_nodes=None, node_signature=None, value=None):
        result_dict = dict(zip(prototypes, [0] * len(prototypes)))
        for prototype_node in prototype_nodes:
            if self._signature_cache[index].get_count(signature=node_signature) < \
                            2*prototype_nodes[prototype_node]["duration"].count:
                distance = prototype_nodes[prototype_node]["duration"].distance(value=value)
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
