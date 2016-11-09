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
    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        for prototype in prototypes:
            node_counts = signature_prototypes.node_count(prototype=prototype)
            for index, node_count in enumerate(node_counts):
                self._monitoring_results_dict[index][prototype] = node_count

    def update_distance(self, prototypes, signature_prototypes, event_type=None, matches=[{}], **kwargs):
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                if signature not in self._measured_nodes[index]:
                    self._update_distances(
                        prototypes=prototypes,
                        index=index,
                        prototype_nodes=matching_prototypes,
                        node_signature=signature
                    )
                    self._measured_nodes[index].add(signature)
        return [match.keys() for match in matches]

    def _update_distances(self, prototypes, index=0, prototype_nodes=None, node_signature=None):
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))

        for prototype_node in prototype_nodes:
            result_dict[prototype_node] = -1
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            base=self._monitoring_results_dict,
            to_add=[result_dict]
        )


class SimpleDistance2(Distance):
    """
    Implementation of SimpleDistance starting with an initial distance of 0.
    """
    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        for prototype in prototypes:
            for index in range(self.signature_count):
                self._monitoring_results_dict[index][prototype] = 0

    def update_distance(self, prototypes, signature_prototypes, event_type=None, matches=[{}], **kwargs):
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                if signature not in self._measured_nodes[index]:
                    self._update_distances(
                        prototypes=prototypes,
                        index=index,
                        prototype_nodes=matching_prototypes,
                        node_signature=signature
                    )
                self._measured_nodes[index].add(signature)
        return [match.keys()[0] for match in matches]

    def finish_distance(self, prototypes, signature_prototypes):
        result_dict = [dict(zip(prototypes, [0] * len(prototypes))) for _ in range(self.signature_count)]

        for prototype in prototypes:
            node_counts = signature_prototypes.node_count(prototype=prototype)
            # matching
            for index, node_count in enumerate(node_counts):
                result_dict[index][prototype] = node_count - (
                    len(self._measured_nodes[index]) -
                    self._monitoring_results_dict[index][prototype])
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            to_add=result_dict,
            base=self._monitoring_results_dict
        )
        return [[value] for monitoring_result in self._monitoring_results_dict for value
                in monitoring_result.values()]

    def _update_distances(self, prototypes, index=0, prototype_nodes=None, node_signature=None):
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))
        for prototype_node in prototype_nodes:
            result_dict[prototype_node] = 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )
