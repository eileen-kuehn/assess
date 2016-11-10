import dengraph.distance
import time

from assess.algorithms.signatures.ensemblesignaturecache import EnsembleSignatureCache
from assess.algorithms.signatures.signaturecache import PrototypeSignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent

from dengraph.utilities.pretty import str_time


class PrototypeWrapper(object):
    def __init__(self, signature_cache, prototype_name):
        self._signature_cache = signature_cache
        self._prototype_name = prototype_name

    def node_count(self, prototype=None):
        return self._signature_cache.node_count()

    def get(self, signature):
        return {self._prototype_name: self._signature_cache.get(signature)}

    def frequency(self, prototype=None):
        return self._signature_cache.frequency()


class ClusterDistance(dengraph.distance.IncrementalDistance):
    def __init__(self, threshold=.1, distance=None):
        self.threshold = threshold
        self.distance = distance

    def __call__(self, first, second, default=None):
        start_time = time.time()
        if isinstance(first, EnsembleSignatureCache):
            first = first.internal()[0]
        if isinstance(second, EnsembleSignatureCache):
            second = second.internal()[0]
        # placeholder prototypes to access data
        prototypes = [first]
        prototypes_cache = PrototypeWrapper(first, prototypes[0])

        self.distance.init_distance(prototypes, prototypes_cache)
        for signature in second:
            matching_prototypes = prototypes_cache.get(signature=signature)
            for statistic in second.get(signature)["duration"]:
                count = statistic.count
                value = statistic.mean
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
        done_time = time.time()
        print('Calculated distance of %s in %s' % (result, str_time(done_time - start_time)))
        return result

    def update(self, first, second, base_distance=0, default=None):
        pass

    def mean(self, *args, **kwargs):
        if len(args) == 1:
            args = args[0]
        return PrototypeSignatureCache.from_signature_caches(args, prototype=1)

    def median(self, *args, **kwargs):
        return NotImplementedError
