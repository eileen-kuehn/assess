"""
The module for StartExitDistance offers classes to determine distances for dynamic trees based
on their start and exit events.
"""

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache


class StartExitDistance(Distance):
    """
    The StartExitDistance offers distance measurement to a given prototype by considering start
    and exit events. For exit events statistics like mean and variance are considered.
    The actual distance starts at the maximum distance possible based on the prototype given.
    """
    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = None  # TODO: why an extra cache?

    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        self._signature_cache = [SignatureCache() for _ in range(self.signature_count)]
        for prototype in prototypes:
            node_count = prototype.node_count()
            for index in range(self.signature_count):
                self._monitoring_results_dict[index][prototype] = node_count

    def update_distance(self, prototypes, signature_prototypes, matches=[{}], value=None, **kwargs):
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
        return [match.keys()[0] for match in matches]

    def node_count(self):
        return [signature_cache.frequency()/2.0 for signature_cache in self._signature_cache]

    def _update_distances(self, prototypes, index=0, prototype_nodes=None, node_signature=None, value=None):
        result_dict = dict(zip(prototypes, [.5] * len(prototypes)))

        for prototype_node in prototype_nodes:
            if self._signature_cache[index].get(signature=node_signature) < \
                            2*prototype_nodes[prototype_node]["duration"].count:
                distance = prototype_nodes[prototype_node]["duration"].distance(value=value)
                if distance is None:
                    result_dict[prototype_node] = -.5
                else:
                    # start element is first considered matching, so -.5
                    # if end element is also matching, [-.5, 0] is added
                    # else ]0, .5] is added to correct the former matching behaviour
                    # FIXME: distance can be infinite, so bound it here
                    if distance == float("inf"):
                        distance = 1
                    result_dict[prototype_node] = -.5 + distance
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )
