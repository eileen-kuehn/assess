from assess.prototypes.simpleprototypes import Tree
from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent
from assess.exceptions.exceptions import EventNotSupportedException, NodeNotFoundException


class TreeInclusionDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)
        self._prototype_dict = {}
        self._monitoring_dict = {}
        self._monitoring_results_dict = {}
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

    def _create_node(self, event):
        parent = self._monitoring_dict.get(event.ppid, None)
        node = self._tree.add_node(
                event.name,
                parent=parent,
                tme=event.tme,
                pid=event.pid,
                ppid=event.ppid)
        self._monitoring_dict[event.pid] = node
        self._update_distances(self._prototypes, self._tree)

    def _update_distances(self, prototypes, tree):
        result_dict = dict(zip(self._prototypes, [0] * len(self._prototypes)))

        for prototype in prototypes:
            result_dict[prototype] = self._calculate_distance(prototype.root(), tree.root())

        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)
        print(self._tree.tree_repr())
        print(self._prototypes[0].tree_repr())
        print("measured distances after %d events: %s" % (
              self._event_counter,
              [value for value in self._monitoring_results_dict.values()]))

    def _perform_calculation(self, prototype, tree):
        distance = 0

        if prototype.name in tree.name:
            # TODO: for all nodes in prototype
            tree_nodes = list(tree.children())
            last_valid_position = 0
            for node in prototype.children():
                for i in range(last_valid_position, len(tree_nodes)):
                    if node.name in tree_nodes[i].name:
                        # matched
                        last_valid_position = i+1
                        distance += self._perform_calculation(node, tree_nodes[i])
                        break
                else:
                    # did not match any node
                    distance += prototype._prototype.subtree_node_count(node)
        else:
            # distance is sum of all nodes
            return prototype._prototype.subtree_node_count(prototype) + tree._prototype.subtree_node_count(tree)
        return distance

    def _calculate_distance(self, prototype, tree):
        distance = 0
        distance += self._perform_calculation(prototype, tree)
        distance += self._perform_calculation(tree, prototype)
        return distance

    def _add_result_dicts(self, first, second):
        #result = dict((key, first[key] + second[key]) for key in set(first.keys() + second.keys()))
        return first
