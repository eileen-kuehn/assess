"""
Module deals with different handlings for distances. Those can easily be attached to algorithms
to adjust calculated distance. Therefore different combinations become available and can easily
be parameterised.
"""


class Distance(object):
    """
    If you plan to implement another distance function, you should subclass this class and write a
    new distance. Base methods that are called are *init_distance* for initialisation or when a new
    tree is started, *update_distance* when a new event has arrived, and *finish_distance* when the
    tree has finished.

    The class itself can be used as an iterator returning the different distances it currently
    stores.
    """
    def __init__(self, prototypes=None):
        self._monitoring_results_dict = {}
        self._prototypes = prototypes
        self._measured_nodes = set()
        self._based_on_original = False

    def __iter__(self):
        for prototype in self._prototypes:
            yield self._monitoring_results_dict.setdefault(prototype, 0)

    def init_distance(self, prototypes=None, signature_prototypes=None):
        """
        This method is just for initialisation purposes. Internal states are reset.

        :param prototypes: The prototypes whose distances are measured.
        """
        self._monitoring_results_dict = {}
        self._measured_nodes = set()

    def update_distance(self, signature=None, matching_prototypes=None, prototypes=None,
                        signature_prototypes=None, **kwargs):
        """
        This method is called whenever a new event has been received.

        :param signature: Signature of the node the event belongs to.
        :param matching_prototypes: The prototypes that actually contain the signature.
        :param prototypes: Reference to the actual prototypes.
        :param signature_prototypes:
        :return: signature
        """
        raise NotImplementedError

    def finish_distance(self, prototypes=None, signature_prototypes=None):
        """
        This method is usually called, when the tree has been finished. It can be used to make
        adaptions/corrections to the calculated distance.

        :param prototypes: Reference to the actual prototypes.
        :param signature_prototypes:
        :return: Array of distances in prototype order.
        """
        raise NotImplementedError

    def node_count(self):
        """
        Returns the count of nodes considered for the actual distance measurement. This count is
        important to calculate the normalised distance with regard to the used distance.

        :return: Count of nodes considered from distance
        """
        return len(self._measured_nodes)

    def is_prototype_based_on_original(self):
        """
        True if the distance is based on the original nodes from the prototypes three, otherwise
        False.

        :return: True if prototype is based on the original tree
        """
        return self._based_on_original

    @staticmethod
    def _add_result_dicts(first, second):
        result = dict((key, first.setdefault(key, 0) + second.setdefault(key, 0))
                      for key in set(first.keys() + second.keys()))
        return result
