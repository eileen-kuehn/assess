import dengraph.distance
import time

from assess.algorithms.signatures.ensemblesignaturecache import EnsembleSignatureCache
from assess.algorithms.signatures.signaturecache import PrototypeSignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent


class SignatureWrapper(object):
    def __init__(self, signature_cache):
        self._signature_cache = signature_cache
        self._key = self._signature_cache.internal().keys()[0]

    def __iter__(self):
        return iter(self._signature_cache)

    def node_count(self):
        if isinstance(self._signature_cache, PrototypeSignatureCache):
            return self._signature_cache.node_count().values()[0]
        return self._signature_cache.node_count()

    def get(self, signature):
        if isinstance(self._signature_cache, PrototypeSignatureCache):
            return self._signature_cache.get(signature).values()[0]
        return self._signature_cache.get(signature)

    def frequency(self):
        return self._signature_cache.frequency()


class PrototypeWrapper(object):
    def __init__(self, signature_cache, prototype_name):
        self._signature_cache = signature_cache
        self._prototype_name = prototype_name

    @property
    def statistics_cls(self):
        return self._signature_cache.statistics_cls

    def __iter__(self):
        return iter(self._signature_cache)

    def node_count(self, prototype=None):
        return self._signature_cache.node_count()

    def get(self, signature):
        # TODO: maybe if function returns empty dict, this one should also?
        if isinstance(self._signature_cache, PrototypeSignatureCache):
            try:
                return {self._prototype_name: self._signature_cache.get(signature).values()[0]}
            except IndexError:
                return {self._prototype_name: None}
        return {self._prototype_name: self._signature_cache.get(signature)}

    def frequency(self, prototype=None):
        return self._signature_cache.frequency()


class ClusterDistance(dengraph.distance.IncrementalDistance):
    def __init__(self, distance, threshold=0):
        self.threshold = threshold
        self.distance = distance

    def __call__(self, first, second, default=None):
        if isinstance(first, EnsembleSignatureCache):
            first = first.internal()[0]
        if isinstance(second, EnsembleSignatureCache):
            second = second.internal()[0]
        # placeholder prototypes to access data
        prototypes = [first]
        prototypes_cache = PrototypeWrapper(first, prototypes[0])
        second = SignatureWrapper(second)

        self.distance.init_distance(prototypes, prototypes_cache)
        for signature in second:
            matching_prototypes = prototypes_cache.get(signature=signature)
            for statistic in second.get(signature)["duration"]:
                count = statistic.count
                value = statistic.value
                for _ in range(count):
                    if self.distance.supported[ProcessStartEvent]:
                        self.distance.update_distance(
                            prototypes=prototypes,
                            signature_prototypes=prototypes_cache,
                            event_type=ProcessStartEvent,
                            matches=[{signature: matching_prototypes}]
                        )
                    if self.distance.supported[ProcessExitEvent]:
                        self.distance.update_distance(
                            prototypes=prototypes,
                            signature_prototypes=prototypes_cache,
                            event_type=ProcessExitEvent,
                            matches=[{signature: matching_prototypes}],
                            value=value
                        )
        self.distance.finish_distance(prototypes, prototypes_cache)
        result = next(self.distance.iter_on_prototypes(prototypes))[0] / float(
            first.frequency() + second.frequency())
        return result

    def update(self, first, second, base_distance=0, default=None):
        pass

    def mean(self, *args, **kwargs):
        if len(args) == 1:
            args = args[0]
        return PrototypeSignatureCache.from_signature_caches(args,
                                                             prototype=1,
                                                             threshold=self.threshold)

    def median(self, *args, **kwargs):
        return NotImplementedError
