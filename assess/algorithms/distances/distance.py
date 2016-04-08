class Distance(object):
    def __init__(self):
        self._monitoring_results_dict = {}
        self._measured_nodes = set()
        self._prototype_node_count = None

    def __iter__(self):
        for value in self._monitoring_results_dict.values():
            yield value

    def init_distance(self, prototypes=None, prototype_node_count=None):
        self._prototype_node_count = prototype_node_count
        self._monitoring_results_dict = {}
        self._measured_nodes = set()

    def update_distance(self, signature=None, matching_prototypes=None, prototypes=None):
        pass

    def finish_distance(self, prototypes=None):
        pass

    def _add_result_dicts(self, first, second):
        result = dict((key, first[key] + second[key]) for key in set(first.keys() + second.keys()))
        return result
