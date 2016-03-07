from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent
from assess.exceptions.exceptions import EventNotSupportedException, NodeNotFoundException


class TreeInclusionDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._monitoring_results = []
        self._event_counter = 0

    def _add_event(self, event, **kwargs):
        # just adding, but not removing nodes
        self._event_counter += 1
        if type(event) is ProcessStartEvent:
            self._create_node(event)
        elif type(event) is ProcessExitEvent:
            pass
        else:
            raise EventNotSupportedException(event)
        return [value for value in self._monitoring_results[-1].values()]

    def _create_node(self, event):
        signature = TreeDistanceAlgorithm._create_node(self, event)
        self._update_distances(self._prototypes, self._tree)
        return signature

    def _update_distances(self, prototypes, tree):
        result_dict = dict(zip(self._prototypes, [0] * len(self._prototypes)))

        for prototype in prototypes:
            result_dict[prototype] = self._calculate_distance(prototype.root(), tree.root())

        # add local node distance to global tree distance
        self._add_result_dicts(result_dict)

    def _perform_calculation(self, prototype, tree):
        distance = 0

        if self._signature.get_signature(prototype, prototype.parent()) in self._signature.get_signature(tree, tree.parent()):
            tree_nodes = list(tree.children())
            last_valid_position = 0
            for node in prototype.children():
                for i in range(last_valid_position, len(tree_nodes)):
                    if self._signature.get_signature(node, node.parent()) in self._signature.get_signature(tree_nodes[i], tree_nodes[i].parent()):
                        # matched
                        last_valid_position = i+1
                        distance += self._perform_calculation(node, tree_nodes[i])
                        break
                else:
                    # did not match any node
                    distance += node.node_count()
        else:
            # distance is sum of all nodes
            return prototype.node_count()
        return distance

    def _calculate_distance(self, prototype, tree):
        distance = 0
        distance += self._perform_calculation(prototype, tree)
        distance += self._perform_calculation(tree, prototype)
        return distance

    def _add_result_dicts(self, results):
        return self._monitoring_results.append(results)
