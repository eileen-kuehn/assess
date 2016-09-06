from collections import deque

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache


class DynamicDistance(Distance):
    def __init__(self, algorithm, max_count=3, wrapped_distance=None):
        Distance.__init__(self, algorithm)
        self._max_count = max_count
        self._wrapped_distance = wrapped_distance(algorithm)
        self._order_cache = {}
        self._last_signatures = deque(maxlen=self._max_count)

    def __iter__(self):
        wrapped_distance = self._wrapped_distance.current_distance()
        for prototype in self._algorithm.prototypes:
            yield self._monitoring_results_dict.setdefault(prototype, 0) + \
                  wrapped_distance.setdefault(prototype, 0)

    def current_distance(self):
        wrapped_distance = self._wrapped_distance.current_distance()
        return self._add_result_dicts(wrapped_distance, self._monitoring_results_dict.copy())

    def init_distance(self):
        Distance.init_distance(self)
        self._wrapped_distance.init_distance()

        # create the order-dependent signature cache for prototypes
        # FIXME: this does not work with current CRs
        for prototype in self._algorithm.prototypes:
            prototype_deque = deque(maxlen=self._max_count)
            for event in prototype.event_iter():
                prototype_deque.append(
                    self._algorithm.signature.get_signature(node=event, parent=None)
                )
                self._order_cache.setdefault(prototype, SignatureCache()).\
                    add_signature("_".join(prototype_deque))
            self._monitoring_results_dict[prototype] = 0

    def _distance_factor(self, prototype):
        # TODO: ich denke das ist noch der falsche Faktor, nachschauen bei den Normalisierungen
        frequency = self._order_cache[prototype].frequency()
        count = self._algorithm.event_counts()[0] + \
            self._algorithm.signature_prototypes.node_count(prototype=prototype)
        return 1 - frequency / float(count + frequency)

    def update_distance(self, signature=None, matching_prototypes=None, **kwargs):
        result = self._wrapped_distance.update_distance(
            signature=signature, matching_prototypes=matching_prototypes, **kwargs)

        self._last_signatures.append(signature)
        result_dict = dict(zip(self._algorithm.prototypes, [0] * len(self._algorithm.prototypes)))
        for prototype in self._algorithm.prototypes:
            result_dict[prototype] = self._distance_factor(prototype) if \
                self._order_cache[prototype].get("_".join(self._last_signatures)) == 0 else 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            result_dict,
            self._monitoring_results_dict
        )
        return result

    def finish_distance(self):
        return self._wrapped_distance.finish_distance()

    def node_count(self):
        return self._wrapped_distance.node_count()
