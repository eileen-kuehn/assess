"""
Module implements a distance that introduces a prediction for missing nodes for the monitoring tree.
"""
from assess.algorithms.distances.distance import Distance


class AdditionalMissingDistance(Distance):
    """
    Class approximates number of missing nodes to measure distance.
    """
    def __init__(self, **kwargs):
        Distance.__init__(self, **kwargs)
        self._additional_nodes_dict = None
        self._missing_nodes_dict = None

    def init_distance(self):
        Distance.init_distance(self)
        self._additional_nodes_dict = [{}] * self._algorithm.signature.count
        self._missing_nodes_dict = [{}] * self._algorithm.signature.count
        for prototype in self._algorithm.prototypes:
            for index in range(self._algorithm.signature.count):
                self._monitoring_results_dict[index][prototype] = 0
                self._additional_nodes_dict[index][prototype] = 0
                self._missing_nodes_dict[index][prototype] = 0

    def update_distance(self, matches=[], **kwargs):
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                if signature not in self._measured_nodes:
                    self._update_additional_distances(
                        index=index,
                        prototype_nodes=matching_prototypes,
                        node_signature=signature
                    )
                self._update_missing_distances(
                    index=index,
                    prototype_nodes=matching_prototypes,
                    node_signature=signature
                )
                self._measured_nodes[index].add(signature)
        return [match.keys()[0] for match in matches]

    def finish_distance(self):
        prototypes = self._algorithm.prototypes
        result_dict = [dict(zip(prototypes, [0] * len(prototypes)))] * self._algorithm.signature.count

        for prototype in prototypes:
            prototype_counts = self._algorithm.signature_prototypes.node_count(prototype=prototype)
            # matching
            for index, prototype_count in enumerate(prototype_counts):
                result_dict[index][prototype] = (prototype_count - (
                    len(self._measured_nodes[index]) -
                    self._additional_nodes_dict[index][prototype])) - (
                    self._monitoring_results_dict[index][prototype] -
                    self._additional_nodes_dict[index][prototype])
        # add local node distance to global tree distance
        # FIXME: this is still a problem
        self._monitoring_results_dict = self._add_result_dicts(
            result_dict,
            self._monitoring_results_dict)

        return [[value] for monitoring_result in self._monitoring_results_dict for value
                in monitoring_result.values()]

    def _update_additional_distances(self, index=0, prototype_nodes=None, node_signature=None):
        prototypes = self._algorithm.prototypes
        result_dict = [dict(zip(prototypes, [1] * len(prototypes)))]

        for prototype_node in prototype_nodes:
            result_dict[index][prototype_node] = 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=result_dict,
            base=self._monitoring_results_dict
        )
        self._additional_nodes_dict = self._add_result_dicts(
            index=index,
            to_add=result_dict,
            base=self._additional_nodes_dict
        )

    def _update_missing_distances(self, index, prototype_nodes=None, node_signature=None):
        prototypes = self._algorithm.prototypes
        result_dict = [dict(zip(prototypes, [1] * len(prototypes)))]
        for prototype_node in prototype_nodes:
            result_dict[index][prototype_node] = 0
        for key in result_dict[index].keys():
            if result_dict[index][key] > 0:
                if self._prototype_weight(index, key, self._algorithm.signature_prototypes) <= 0:
                    result_dict[index][key] = 0
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=result_dict,
            base=self._monitoring_results_dict
        )
        self._missing_nodes_dict = self._add_result_dicts(
            index=index,
            to_add=result_dict,
            base=self._missing_nodes_dict
        )

    def _prototype_weight(self, index, prototype, signature_prototypes):
        return 0.9 * signature_prototypes.node_count(prototype=prototype)[index] - \
               self._missing_nodes_dict[index][prototype] - (len(self._measured_nodes[index]) -
                                                      self._additional_nodes_dict[index][prototype])
        # return min(self.node_count_for_prototype(
        #     prototype, original=False),
        #     len(self._measured_nodes)
        # )
        # return min(
        #     self.node_count_for_prototype(prototype, original=False),
        #     (len(self._measured_nodes)-self._additional_nodes_dict[prototype])
