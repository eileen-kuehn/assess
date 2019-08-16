from collections import deque

from assess.algorithms.distances.distance import Distance
from assess.algorithms.signatures.signaturecache import SignatureCache


class DynamicDistance(Distance):
    __slots__ = ("_max_count", "_wrapped_distance", "_order_cache", "_last_signatures")

    def __init__(self, max_count=3, wrapped_distance=None, **kwargs):
        Distance.__init__(self, **kwargs)
        self._max_count = max_count
        self._wrapped_distance = wrapped_distance(**kwargs)
        self._order_cache = None
        self._last_signatures = None

    def __iter__(self):
        wrapped_distance = self._wrapped_distance.current_distance()
        for prototype in self._algorithm.prototypes:
            yield self._monitoring_results_dict.setdefault(prototype, 0) \
                + wrapped_distance.setdefault(prototype, 0)

    def current_distance(self):
        wrapped_distance = self._wrapped_distance.current_distance()
        return self._add_result_dicts(wrapped_distance,
                                      self._monitoring_results_dict.copy())

    def init_distance(self, prototypes, signature_prototypes):
        super().init_distance(prototypes, signature_prototypes)
        self._wrapped_distance.init_distance(prototypes, signature_prototypes)
        self._order_cache = [{} for _ in range(self.signature_count)]
        self._last_signatures = [deque(maxlen=self._max_count)] * self.signature_count

        # create the order-dependent signature cache for prototypes
        # FIXME: this does not work with current CRs
        for prototype in prototypes:
            prototype_deque = deque(maxlen=self._max_count)
            for index, signature in enumerate(self._algorithm.signature):
                for event in prototype.event_iter(supported=self.supported):
                    prototype_deque.append(
                        signature.get_signature(node=event, parent=None)
                    )
                    self._order_cache[index].setdefault(prototype, SignatureCache()).\
                        add_signature("_".join(prototype_deque))
                self._monitoring_results_dict[index][prototype] = 0

    def _distance_factor(self, index, prototype):
        # TODO: ich denke das ist noch der falsche Faktor,
        # nachschauen bei den Normalisierungen
        frequency = self._order_cache[index][prototype].frequency()
        # FIXME: does not fit here...
        count = self._algorithm.event_counts()[0] + \
            self._algorithm.signature_prototypes.node_count(prototype=prototype)
        return 1 - frequency / float(count + frequency)

    def update_distance(self, prototypes, signature_prototypes, event_type=None,
                        matches=None, **kwargs):
        if matches is None:
            matches = []
        result_dict = [dict(zip(self._algorithm.prototypes, [0] * len(
            prototypes))) for _ in range(self.signature_count)]

        for index, match in enumerate(matches):
            for signature, matching_prototypes in match.items():
                if signature is None:
                    continue
                result = self._wrapped_distance.update_distance(
                    prototypes=prototypes,
                    signature=signature,
                    matching_prototypes=matching_prototypes,
                    **kwargs)
                self._last_signatures[index].append(signature)
                for prototype in prototypes:
                    result_dict[index][prototype] = self._distance_factor(
                        index, prototype) if self._order_cache[index][prototype].get(
                            "_".join(self._last_signatures)) == 0 else 0
        # add local node distance to global tree distance
        self._monitoring_results_dict = self._add_result_dicts(
            to_add=result_dict,
            base=self._monitoring_results_dict
        )
        return result

    def finish_distance(self, prototpyes, signature_prototypes):
        return self._wrapped_distance.finish_distance(prototpyes, signature_prototypes)

    def node_count(self, prototypes=None, signature_prototypes=None, by_event=False):
        return self._wrapped_distance.node_count(prototypes, signature_prototypes)
