"""
The module for StartExitDistance offers classes to determine distances for dynamic trees based
on their start and exit events.
"""

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache
from assess.events.events import ProcessStartEvent


class StartExitDistance(Distance):
    """
    The StartExitDistance offers distance measurement to a given prototype by considering start
    and exit events. For exit events statistics like mean and variance are considered.
    The actual distance starts at the maximum distance possible based on the prototype given.

    The distance can be paramertised by defining the weight of either node matching or parameter
    matching. This weight is in the range [0, 1].
    The default weight is at 0.5, meaning, that both nodes and their attributes are equally
    weighted.

    * A weight of 1 means, that only nodes are considered.
    * A weight of zero means, that only attributes are considered.
    """
    def __init__(self, weight=.5, **kwargs):
        Distance.__init__(self, **kwargs)
        self._based_on_original = True
        self._signature_cache = None
        assert 0 <= weight <= 1
        self._weight = weight

    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        self._signature_cache = [SignatureCache(statistics_cls=signature_prototypes.statistics_cls)
                                 for _ in range(self.signature_count)]
        for prototype in prototypes:
            for index in range(self.signature_count):
                node_count = signature_prototypes.frequency(prototype)
                try:
                    self._monitoring_results_dict[index][prototype] = node_count[index]
                except TypeError:
                    self._monitoring_results_dict[index][prototype] = node_count

    def update_distance(self, prototypes, signature_prototypes, event_type, matches=[{}],
                        value=None, **kwargs):
        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                self._update_distances(
                    prototypes=prototypes,
                    event_type=event_type,
                    index=index,
                    prototype_nodes=matching_prototypes,
                    node_signature=signature,
                    value=value
                )
        if event_type == ProcessStartEvent:
            self._signature_cache[index].add_signature(signature=signature)
        else:
            self._signature_cache[index].add_signature(signature=signature,
                                                       value={"duration": value})
        return [match.keys()[0] for match in matches]

    def node_count(self, prototypes=None, signature_prototypes=None):
        if prototypes:
            return [signature_prototypes.frequency(prototype=prototype) for prototype in prototypes]
        return [signature_cache.frequency() for signature_cache in self._signature_cache]

    def _update_distances(self, prototypes, event_type=None, index=0, prototype_nodes=None,
                          node_signature=None, value=None):
        weight = 2 * self._weight  # two times, because looking at start and exit
        # because we have to consider signatures from start and exit, we need to deal with
        # the half of the given weight here
        base = weight / 2.0
        node_base = base
        if event_type != ProcessStartEvent:
            property_base = 2 - weight
            base += property_base
        result_dict = dict(zip(prototypes, [base] * len(prototypes)))

        for prototype_node in prototype_nodes:
            if prototype_nodes[prototype_node] is None:
                continue
            result = 0
            if self._signature_cache[index].get_count(signature=node_signature) < \
                            prototype_nodes[prototype_node]["count"]:
                result -= node_base
            else:
                result += node_base
            if event_type != ProcessStartEvent:
                try:
                    signature_count = self._signature_cache[index].get(
                        signature=node_signature)["duration"].count(value=value)
                except KeyError:
                    # no data has been saved for duration, first exit event
                    signature_count = 0
                except ValueError:
                    # no data has been saved for node_signature
                    signature_count = 0
                distance = prototype_nodes[prototype_node]["duration"].distance(
                    value=value,
                    count=signature_count
                )
                if distance > 0:
                    # partial or full mismatch
                    result += distance * property_base
                else:
                    result -= property_base
            result_dict[prototype_node] = result
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )
