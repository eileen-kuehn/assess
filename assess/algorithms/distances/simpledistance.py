"""
This module offers implementation for SimpleDistance. There are different methods that are
implemented. One does start with a distance of 0 and the other with a distance initialised with
the number of nodes within the prototypes.
"""
from assess.algorithms.distances.distance import Distance


class SimpleDistance(Distance):
    """
    SimpleDistance class implements an exact measure by initialising the distance with the number of
    nodes inside the prototype. For each signature (that has not been checked before) the base
    distance is initialised with one. If the signature does match a prototype, the distance is set
    to -1. This distance measure has the property, that it is rising and falling. Maybe not adequate
    for anomaly detection but it delivers exact results without considering a final step.

    The currently implemented formula is the following:
    * Explicit version: $\delta = |H(P)| - |H(T_{i})| + 2|H(T^{\mathrm{add}}_{i})|$
    * Recursive version: Too long ;)
    """
    def init_distance(self, prototypes=None, signature_prototypes=None):
        Distance.init_distance(
            self, prototypes=prototypes,
            signature_prototypes=signature_prototypes
        )
        for prototype in prototypes:
            self._monitoring_results_dict[prototype] = signature_prototypes.node_count(
                prototype=prototype
            )

    def update_distance(self, signature=None, matching_prototypes=None, prototypes=None,
                        signature_prototypes=None, **kwargs):
        if signature not in self._measured_nodes:
            self._update_distances(
                prototype_nodes=matching_prototypes,
                node_signature=signature,
                prototypes=prototypes,
                signature_prototypes=signature_prototypes
            )
            self._measured_nodes.add(signature)
        return signature

    def finish_distance(self, prototypes=None, signature_prototypes=None):
        pass

    def _update_distances(self, prototype_nodes=None, node_signature=None, prototypes=None,
                          signature_prototypes=None):
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))
        for prototype_node in prototype_nodes:
            result_dict[prototype_node] = -1
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            result_dict,
            self._monitoring_results_dict
        )


class SimpleDistance2(Distance):
    """
    Implementation of SimpleDistance starting with an initial distance of 0.
    """
    def init_distance(self, prototypes=None, signature_prototypes=None):
        Distance.init_distance(
            self,
            prototypes=prototypes,
            signature_prototypes=signature_prototypes
        )
        for prototype in prototypes:
            self._monitoring_results_dict[prototype] = 0

    def update_distance(self, signature=None, matching_prototypes=None, prototypes=None,
                        signature_prototypes=None):
        if signature not in self._measured_nodes:
            self._update_distances(
                prototype_nodes=matching_prototypes,
                node_signature=signature,
                prototypes=prototypes,
                signature_prototypes=signature_prototypes
            )
            self._measured_nodes.add(signature)
        return signature

    def finish_distance(self, prototypes=None, signature_prototypes=None):
        result_dict = dict(zip(prototypes, [0] * len(prototypes)))
        for prototype in prototypes:
            result_dict[prototype] = signature_prototypes.node_count(prototype=prototype) - \
                                     (len(self._measured_nodes) -
                                      self._monitoring_results_dict[prototype])
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            result_dict,
            self._monitoring_results_dict
        )
        return [value for value in self._monitoring_results_dict.values()]

    def _update_distances(self, prototype_nodes=None, node_signature=None, prototypes=None,
                          signature_prototypes=None):
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))
        for prototype_node in prototype_nodes:
            result_dict[prototype_node] = 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            result_dict,
            self._monitoring_results_dict
        )
