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
    def __init__(self, algorithm):
        self._algorithm = algorithm

        self._monitoring_results_dict = None
        self._measured_nodes = None
        self._based_on_original = False

    def __iter__(self):
        """
        Result looks like this: [e_1, ..., e_n] for prototypes
        So first yield, yields all prototypes data for first ensemble.

        Together you get: [[p1e1, ..., p1en], ..., [pne1, ..., pnen]]

        :return:
        """
        for prototype in self._algorithm.prototypes:
            yield [result.setdefault(prototype, 0) for result in self._monitoring_results_dict]

    def current_distance(self):
        return self._monitoring_results_dict.copy()

    def init_distance(self):
        """
        This method is just for initialisation purposes. Internal states are reset.
        """
        count = self._algorithm.signature.count
        self._monitoring_results_dict = [{} for _ in range(count)]
        self._measured_nodes = [set() for _ in range(count)]

    def update_distance(self, matches=[{}], **kwargs):
        """
        This method is called whenever a new event has been received.

        :param matches: List of dictionaries that relates a token to a list of matching prototypes.
        :param kwargs:
        :return: list of signatures
        """
        raise NotImplementedError

    def finish_distance(self):
        """
        This method is usually called, when the tree has been finished. It can be used to make
        adaptions/corrections to the calculated distance.

        :return: Array of distances in prototype order.
        """
        raise NotImplementedError

    def node_count(self):
        """
        Returns the count of nodes considered for the actual distance measurement. This count is
        important to calculate the normalised distance with regard to the used distance.

        Returned format looks like: [v1e1, ..., vnen]

        :return: Count of nodes considered from distance
        """
        return [len(measured_nodes) for measured_nodes in self._measured_nodes]

    def is_prototype_based_on_original(self):
        """
        True if the distance is based on the original nodes from the prototypes three, otherwise
        False.

        :return: True if prototype is based on the original tree
        """
        return self._based_on_original

    @staticmethod
    def _add_result_dicts(base=None, to_add=None, index=None):
        if index is None:
            result = []
            for index, element in enumerate(base):
                result.append(dict((key, element.setdefault(key, 0) + to_add[index].setdefault(key, 0))
                                   for key in set(element.keys() + to_add[index].keys())))
        else:
            result = base
            for element in to_add:
                for key in element.keys():
                    result[index][key] = result[index].get(key, 0) + element.get(key, 0)
        return result

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        # FIXME: maybe this needs to be something else here...
        obj_dict["_measured_nodes"] = [set()] * self._algorithm.signature.count
        return obj_dict
