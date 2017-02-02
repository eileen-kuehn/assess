"""
The module for StartExitDistance offers classes to determine distances for dynamic trees based
on their start and exit events.
"""

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


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
                if signature is None:
                    continue
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

    def node_count(self, prototypes=None, signature_prototypes=None, signature=False):
        if prototypes:
            return [signature_prototypes.frequency(prototype=prototype) for prototype in prototypes]
        if signature:
            return [signature_cache.node_count() for signature_cache in self._signature_cache]
        return [signature_cache.frequency() for signature_cache in self._signature_cache]

    def _update_distances(self, prototypes, event_type=None, index=0, prototype_nodes=None,
                          node_signature=None, value=None):
        if event_type == TrafficEvent:
            factor = 1.0
        else:
            factor = 2.0
        weight = factor * self._weight  # two times, because looking at start and exit
        # because we have to consider signatures from start and exit, we need to deal with
        # the half of the given weight here
        base = self._weight
        node_base = base
        property_base = 0
        if event_type != ProcessStartEvent:
            property_base = factor - weight
            base += property_base
        result_dict = dict(zip(prototypes, [base for _ in range(len(prototypes))]))

        for prototype_node in prototype_nodes:
            if prototype_nodes[prototype_node] is None:
                continue
            result = 0
            if self._signature_cache[index].get_count(signature=node_signature) < \
                            prototype_nodes[prototype_node]["count"]:
                result -= node_base
            else:
                result += node_base
            if property_base > 0:
                try:
                    signature_count = self._signature_cache[index].get(
                        signature=node_signature)["duration"].count(value=value)
                except (KeyError, ValueError, TypeError):
                    # no data has been saved for node_signature
                    signature_count = 0
                try:
                    distance = prototype_nodes[prototype_node]["duration"].distance(
                        value=value,
                        count=signature_count
                    )
                except KeyError:
                    distance = 1
                if distance > 0.5:
                    # partial or full mismatch
                    result += distance * property_base
                else:
                    if distance is None:
                        distance = 0
                    result -= (1 - distance) * property_base
            result_dict[prototype_node] = result
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            index=index,
            to_add=[result_dict],
            base=self._monitoring_results_dict
        )

    def __repr__(self):
        return "%s (weight=%s)" % (self.__class__.__name__, self._weight)
