class Distance(object):
    """
    If you plan to implement another distance function, you should subclass dist class and write a new distance.
    Base methods that are called are *init_distance* for initialisation or when a new tree is started,
    *update_distance* when a new event has arrived, and *finish_distance* when the tree has finished.

    The class itself can be used as an iterator returning the different distances it currently stores.
    """
    def __init__(self):
        self._monitoring_results_dict = {}
        self._measured_nodes = set()
        self._prototype_node_count = None
        self._based_on_original = False

    def __iter__(self):
        for value in self._monitoring_results_dict.values():
            yield value

    def init_distance(self, prototypes=None, prototype_node_count=None):
        """
        This method is just for initialisation purposes. Internal states are reset.
        :param prototypes: The prototypes whose distances are measured.
        :param prototype_node_count: A reference to the method to determine the nodes per prototype.
        """
        self._prototype_node_count = prototype_node_count
        self._monitoring_results_dict = {}
        self._measured_nodes = set()

    def update_distance(self, signature=None, matching_prototypes=None, prototypes=None, **kwargs):
        """
        This method is called whenever a new event has been received.
        :param signature: Signature of the node the event belongs to.
        :param matching_prototypes: The prototypes that actually contain the signature.
        :param prototypes: Reference to the actual prototypes.
        :return: signature
        """
        pass

    def finish_distance(self, prototypes=None):
        """
        This method is usually called, when the tree has been finished. It can be used to make adaptions/corrections
        to the calculated distance.
        :param prototypes: Reference to the actual prototypes.
        :return: Array of distances in prototype order.
        """
        pass

    def node_count(self):
        return len(self._measured_nodes)

    def is_prototype_based_on_original(self):
        return self._based_on_original

    def _add_result_dicts(self, first, second):
        result = dict((key, first[key] + second[key]) for key in set(first.keys() + second.keys()))
        return result
