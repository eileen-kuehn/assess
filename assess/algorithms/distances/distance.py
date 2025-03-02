"""
Module deals with different handlings for distances. Those can easily be attached
to algorithms to adjust calculated distance. Therefore different combinations
become available and can easily be parameterised.
"""
from typing import Dict

from assess.events.events import ProcessExitEvent, ProcessStartEvent, TrafficEvent, \
    ParameterEvent, Event


class Distance(object):
    """
    If you plan to implement another distance function, you should subclass this
    class and write a new distance. Base methods that are called are *init_distance*
    for initialisation or when a new tree is started, *update_distance* when a
    new event has arrived, and *finish_distance* when the tree has finished.

    The class itself can be used as an iterator returning the different distances
    it currently stores.
    """
    __slots__ = ("_monitoring_results_dict", "_measured_nodes", "_based_on_original",
                 "signature_count", "supported")

    def __init__(self, signature_count: int=1):
        """
        :param signature_count: The count of signatures that are processed
        """
        self._monitoring_results_dict = None
        self._measured_nodes = None
        self._based_on_original = False
        self.signature_count: int = signature_count
        self.supported: Dict[Event, bool] = {
            ProcessStartEvent: True,
            ProcessExitEvent: True,
            TrafficEvent: False,
            ParameterEvent: False
        }

    def iter_on_prototypes(self, prototypes=None):
        """
        Result looks like this: [e_1, ..., e_n] for prototypes
        So first yield, yields all prototypes data for first ensemble.

        Together you get: [[p1e1, ..., p1en], ..., [pne1, ..., pnen]]

        :return:
        """
        for prototype in prototypes:
            yield [result.setdefault(prototype, 0) for result in
                   self._monitoring_results_dict]

    def distance_for_prototypes(self, prototypes):
        """
        Format is like [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]

        :return: formatted distance
        """
        result = [value for value in self.iter_on_prototypes(prototypes)]
        return [list(element) for element in zip(*result)]

    def current_distance(self):
        return self._monitoring_results_dict.copy()

    def init_distance(self, prototypes, signature_prototypes):
        """
        This method is just for initialisation purposes. Internal states are reset.
        """
        self._monitoring_results_dict = [{} for _ in range(self.signature_count)]
        self._measured_nodes = [set() for _ in range(self.signature_count)]

    def update_distance(self, prototypes, signature_prototypes, event_type=None,
                        matches=None, **kwargs):
        """
        This method is called whenever a new event has been received.

        :param matches: List of dictionaries that relates a token to a list of
            matching prototypes.
        :param kwargs:
        :return: list of signatures
        """
        raise NotImplementedError

    def finish_distance(self, prototypes, signature_prototypes):
        """
        This method is usually called, when the tree has been finished. It can
        be used to make adaptions/corrections to the calculated distance.

        :return: Array of distances in prototype order.
        """
        pass

    def weights(self):
        """
        This method returns a dict of weights for the different support keys
        being used internally. Based on this weighting, the influence of different
        kinds of events can be evaluated.

        Returned format looks like: {support_key: weight, ...}

        :return: Dict of weights
        """
        # FIXME: implement me!
        return NotImplemented

    def event_count(self, by_event=False):
        return [len(measured_nodes) for measured_nodes in self._measured_nodes]

    def node_count(self, prototypes=None, signature_prototypes=None,
                   signature=False, by_event=False):
        """
        Returns the count of nodes considered for the actual distance measurement.
        This count is important to calculate the normalised distance with regard
        to the used distance.

        Returned format looks like: [v1e1, ..., vnen]

        This method always at least returns a count of 0. Also if the distance
        itself was not initialised, still 0 is returned.

        FIXME:
        If signature is true, then the frequency of nodes is ignored and only
        the actual count is returned. This is a dirty fix for now...

        :return: Count of nodes considered from distance
        """
        if prototypes is not None:
            return [signature_prototypes.node_count(prototype=prototype)
                    for prototype in prototypes]
        return [len(measured_nodes) for measured_nodes in self._measured_nodes]

    def is_prototype_based_on_original(self):
        """
        True if the distance is based on the original nodes from the prototypes
        three, otherwise False.

        :return: True if prototype is based on the original tree
        """
        return self._based_on_original

    @staticmethod
    def _add_result_dicts(base=None, to_add=None, index=None):
        if index is None:
            result = []  # ensemble
            for index, element in enumerate(base):
                result.append(
                    dict(
                        (
                            key,
                            element.get(key, 0) + to_add[index].get(key, 0)
                        )
                        for key in {*element, *to_add[index]}))
        else:
            result = base
            for element in to_add:
                for key in element.keys():
                    result[index][key] = result[index].get(key, 0) + element.get(key, 0)
        return result

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        # FIXME: maybe this needs to be something else here...
        obj_dict["_measured_nodes"] = [set()] * self.signature_count
        return obj_dict

    def __repr__(self):
        return "%s" % self.__class__.__name__
