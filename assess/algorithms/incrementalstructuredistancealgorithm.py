from assess.prototypes.simpleprototypes import *
from assess.events.events import *
from assess.exceptions.exceptions import *
from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm


class IncrementalStructureDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self):
        TreeDistanceAlgorithm.__init__(self)
        self._prototype_dict = {}
        self._monitoring_tree = Tree()
        self._monitoring_dict = {}
        self._monitoring_results_dict = {}
        self._event_counter = 0

    @TreeDistanceAlgorithm.prototypes.setter
    def prototypes(self, value=None):
        for prototype in value:
            # store links to nodes based on position into dictionary
            for process in prototype.nodes():
                # TODO: handle collisions
                depth = process.depth()
                if depth == 0:
                    # root processes
                    name = "%d" % depth
                else:
                    neighbors = process.parent().children()
                    count = self._node_number_on_layer(process, neighbors)
                    name = "%s.%d" % (process.parent().algorithm_id, count)
                process.algorithm_id = name
                # TODO: several should be able to be stored here
                self._prototype_dict[name] = [process]
            # initialize default distance to prototypes
            self._monitoring_results_dict[prototype] = 0
        print(self._prototype_dict)
        TreeDistanceAlgorithm.prototypes.__set__(self, value)

    def _node_number_on_layer(self, process, neighboring_processes):
        count = 0
        for node in neighboring_processes:
            count += 1
            if node == process:
                return count
        raise NodeNotFoundException(process, neighboring_processes)

    def _add_event(self, event, **kwargs):
        self._event_counter += 1
        if type(event) is ProcessStartEvent:
            self._create_process(event)
        elif type(event) is ProcessExitEvent:
            self._finish_process(event)
        elif type(event) is TrafficEvent:
            self._add_traffic(event)
        else:
            raise EventNotSupportedException(event)

    def _create_process(self, event):
        parent = self._monitoring_dict.get(event.ppid, None)
        node = self._monitoring_tree.add_node(
                "0" if parent is None else "%s.%d" % (parent.name, parent.child_count() + 1),
                parent=parent,
                tme=event.tme,
                pid=event.pid,
                ppid=event.ppid,
                processname=event.name)
        # TODO: whenever pid is not unique, I will overwrite value
        self._monitoring_dict[event.pid] = node
        self._update_distances(self._prototype_dict.get(node.name, []), node)
        print(node.name)
        print([node.algorithm_id for node in self._prototypes[0].nodes()])
        print("measured distances after %d events: %s" % (
              self._event_counter,
              [value for value in self._monitoring_results_dict.values()]))

    def _finish_process(self, event):
        # just ignoring the exit event of processes here
        pass

    def _add_traffic(self, event):
        raise NotImplementedError

    def _update_distances(self, prototype_nodes, monitoring_node):
        result_dict = dict(zip(self._prototypes, [1] * len(self._prototypes)))
        for prototype_node in prototype_nodes:
            if monitoring_node.name in prototype_node.algorithm_id:
                result_dict[prototype_node._prototype] = 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(result_dict, self._monitoring_results_dict)

    def _add_result_dicts(self, first, second):
        result = dict((key, first[key] + second[key]) for key in set(first.keys() + second.keys()))
        return result
