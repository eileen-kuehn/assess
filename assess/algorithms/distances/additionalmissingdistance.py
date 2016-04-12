from assess.algorithms.distances.distance import Distance


class AdditionalMissingDistance(Distance):
    def __init__(self):
        Distance.__init__(self)
        self._additional_nodes_dict = {}
        self._missing_nodes_dict = {}

    def init_distance(self, prototypes=None, prototype_node_count=None):
        Distance.init_distance(self, prototype_node_count=prototype_node_count)
        for prototype in prototypes:
            self._monitoring_results_dict[prototype] = 0
            self._additional_nodes_dict[prototype] = 0
            self._missing_nodes_dict[prototype] = 0

    def update_distance(self, signature=None, matching_prototypes=None, prototypes=None):
        if signature not in self._measured_nodes:
            self._update_additional_distances(
                prototype_nodes=matching_prototypes,
                node_signature=signature,
                prototypes=prototypes
            )
        self._update_missing_distances(
            prototype_nodes=matching_prototypes,
            node_signature=signature,
            prototypes=prototypes
        )
        self._measured_nodes.add(signature)
        return signature

    def finish_distance(self, prototypes=None):
        result_dict = dict(zip(prototypes, [0] * len(prototypes)))
        for prototype in prototypes:
            prototype_count = self._prototype_node_count(prototype, original=False)
            # matching
            result_dict[prototype] = (prototype_count - (len(self._measured_nodes) - self._additional_nodes_dict[prototype])) - \
                                     (self._monitoring_results_dict[prototype] - self._additional_nodes_dict[prototype])
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)
        return [value for value in self._monitoring_results_dict.values()]

    def _update_additional_distances(self, prototype_nodes=None, node_signature=None, prototypes=None):
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))
        for prototype_node in prototype_nodes:
            result_dict[prototype_node] = 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)
        self._additional_nodes_dict = self._add_result_dicts(result_dict, self._additional_nodes_dict)

    def _update_missing_distances(self, prototype_nodes=None, node_signature=None, prototypes=None):
        result_dict = dict(zip(prototypes, [1] * len(prototypes)))
        for prototype_node in prototype_nodes:
            result_dict[prototype_node] = 0
        for key in result_dict.keys():
            if result_dict[key] > 0:
                if self._prototype_weight(key) <= 0:
                    result_dict[key] = 0
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)
        self._missing_nodes_dict = self._add_result_dicts(result_dict, self._missing_nodes_dict)

    def _prototype_weight(self, prototype):
        return 0.9 * self._prototype_node_count(prototype, original=False) - self._missing_nodes_dict[prototype] - \
               (len(self._measured_nodes) - self._additional_nodes_dict[prototype])
        # return min(self.node_count_for_prototype(prototype, original=False), len(self._measured_nodes))
        # return min(
        #     self.node_count_for_prototype(prototype, original=False),
        #     (len(self._measured_nodes)-self._additional_nodes_dict[prototype])