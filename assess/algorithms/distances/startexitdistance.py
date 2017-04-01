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
        self._based_on_original = False
        self._signature_cache = None
        assert 0 <= weight <= 1
        self._weight = weight
        self._cached_weights = None

    def init_distance(self, prototypes, signature_prototypes):
        Distance.init_distance(self, prototypes, signature_prototypes)
        self._signature_cache = [SignatureCache(statistics_cls=signature_prototypes.statistics_cls,
                                                supported=self.supported)
                                 for _ in range(self.signature_count)]
        for prototype in prototypes:
            for index in range(self.signature_count):
                node_count = signature_prototypes.multiplicity(prototype=prototype)
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
                    self._signature_cache[index][signature, ProcessStartEvent] = {"count": 0}
                else:
                    self._signature_cache[index][signature, event_type] = {"count": 0, "duration": value}
        return [match.keys()[0] for match in matches]

    def node_count(self, prototypes=None, signature_prototypes=None, signature=False, by_event=False):
        if prototypes:
            return [signature_prototypes.multiplicity(prototype=prototype, by_event=by_event) for prototype in prototypes]
        if signature:
            return [signature_cache.node_count() for signature_cache in self._signature_cache]
        return [signature_cache.multiplicity(by_event=by_event) for signature_cache in self._signature_cache]

    def event_count(self, by_event=False):
        return [signature_cache.multiplicity(by_event=by_event) for signature_cache in
                self._signature_cache]

    def weights(self):
        if self._cached_weights is None:
            self._cached_weights = {}
            for support_key in self.supported:
                if support_key == TrafficEvent:
                    factor = 1.0
                else:
                    factor = 2.0
                weight = factor * self._weight
                base = self._weight
                if support_key != ProcessStartEvent:
                    property_base = factor - weight
                    base += property_base
                self._cached_weights[support_key] = base
        return self._cached_weights

    def _update_distances(self, prototypes, event_type=None, index=0, prototype_nodes=None,
                          node_signature=None, value=None):
        base = self.weights().get(event_type, 0)
        node_base = self._weight
        property_base = base - node_base
        result_dict = dict.fromkeys(prototypes, base)

        for prototype_node in prototype_nodes:
            if prototype_nodes[prototype_node] is None:
                continue
            result = 0
            if self._signature_cache[index].multiplicity(signature=node_signature, event_type=event_type) < \
                            prototype_nodes[prototype_node][event_type]["count"].count():
                result -= node_base
            else:
                result += node_base
            if property_base > 0:
                try:
                    signature_count = self._signature_cache[index].get_statistics(
                        signature=node_signature, key="duration", event_type=event_type).count(
                        value=value)
                except (KeyError, ValueError, TypeError):
                    # no data has been saved for node_signature
                    signature_count = 0
                try:
                    distance = prototype_nodes[prototype_node][event_type]["duration"].distance(
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
