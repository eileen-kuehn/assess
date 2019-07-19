import math

import dengraph.distance
from assess.algorithms.distances.ensembledistance import mean_ensemble_distance

from assess.algorithms.signatures.ensemblesignaturecache import *
from assess.algorithms.signatures.signaturecache import *


class SignatureWrapper(object):
    def __init__(self, signature_cache):
        self._signature_cache = signature_cache

    def __iter__(self):
        return iter(self._signature_cache)

    def node_count(self):
        if isinstance(self._signature_cache, PrototypeSignatureCache):
            return self._signature_cache.node_count()
        return self._signature_cache.node_count()

    def get(self, signature):
        result = self._signature_cache.get(signature)
        if not isinstance(result, list):
            result = EnsembleSignatureCacheList(result)
        return result

    def multiplicity(self):
        return self._signature_cache.multiplicity()


class PrototypeWrapper(object):
    def __init__(self, signature_cache, prototype_name):
        self._signature_cache_list = signature_cache  # this is a list of caches!
        self.prototype_name = prototype_name

    @property
    def statistics_cls(self):
        return self._signature_cache_list[0].statistics_cls

    def __iter__(self):
        return iter(self._signature_cache_list)

    def node_count(self, prototype=None):
        return self._signature_cache_list.node_count()

    def get(self, signature):
        result = []
        if isinstance(self._signature_cache_list[0], PrototypeSignatureCache):
            assert False
            try:
                # overwriting the original name of prototype
                result.append(self._signature_cache_list.get(signature))
            except IndexError:
                result.append({})
        elif isinstance(self._signature_cache_list[0], EnsembleSignatureCache):
            # p_1 {e_1, ..., e_n}, ... p_2 {e_1, ..., e_n}
            tmp = [cache.get(signature) for cache in self._signature_cache_list]
            result = [{} for _ in range(len(signature))]
            for prototype_idx, prototype in enumerate(tmp):
                for ensemble_idx, ensemble in enumerate(prototype):
                    result[ensemble_idx].setdefault(signature[ensemble_idx], {})[self.prototype_name[prototype_idx]] = ensemble
        return result

    def multiplicity(self, prototype=None):
        if prototype is not None:
            return prototype.multiplicity()
        return EnsemblePrototypeSignatureCacheList(cache.multiplicity() for cache in self._signature_cache_list)


class ClusterDistance(dengraph.distance.IncrementalDistance):
    def __init__(self, distance, threshold=0):
        self.threshold = threshold
        self.distance = distance

    def __call__(self, prototypes, second, default=None):
        """
        :param prototypes: List of prototypes to be checked; may include cluster representatives
        :param second: Current tree to be checked
        :param default: Default distance to return
        :return: (Minimal) distance between first and second (if first includes several CRs)
        """
        result = default
        # placeholder prototypes to access data
        if not isinstance(prototypes, list):
            prototypes = [prototypes]
        prototypes_caches = PrototypeWrapper(prototypes, prototypes)
        second = SignatureWrapper(second)
        self.distance.init_distance(prototypes, prototypes_caches)

        # TODO: update distance with regard to all signatures and related statistics (count, duration, value)

        for signature in second:
            matching_prototypes = prototypes_caches.get(signature=signature)
            supporters = second.get(signature=signature)
            for supporter_index, supporter in enumerate(supporters):
                # each ensemble identity class needs to be handled separately
                if supporter is None:
                    # skip supporters that don't match anything
                    continue
                for support_key, statistics in supporter.items():
                    if len(statistics.keys()) <= 1:
                        # I am only considering count here
                        statistic = statistics.get("count", [])
                        for stat in statistic:
                            count = int(math.ceil(stat.count))  # round up to always consider occurrence
                            for _ in range(count):
                                # select for matches only specific signature
                                self.distance.update_distance(
                                    prototypes=prototypes_caches.prototype_name,
                                    signature_prototypes=prototypes_caches,
                                    event_type=support_key,
                                    matches=[matching_prototypes[idx] if idx == supporter_index else {} for idx, value in enumerate(matching_prototypes)]
                                )
                    else:
                        # only considering duration here
                        statistic = statistics.get("duration", [])
                        for stat in statistic:
                            count = int(math.ceil(stat.count))  # round up to always consider occurrence
                            for _ in range(count):
                                self.distance.update_distance(
                                    prototypes=prototypes_caches.prototype_name,
                                    signature_prototypes=prototypes_caches,
                                    event_type=support_key,
                                    matches=[matching_prototypes[idx] if idx == supporter_index else {} for idx, value in enumerate(matching_prototypes)]
                                )
        self.distance.finish_distance(prototypes, prototypes_caches)
        results = self.distance.distance_for_prototypes(prototypes)
        normalised_results = []
        event_counts = prototypes_caches.multiplicity()
        tree_event_counts = second.multiplicity()
        for i, ensemble in enumerate(results):
            for j, prototype in enumerate(ensemble):
                normalised_results.append([2 * results[i][j] / float(event_counts[j][i] + tree_event_counts[i] + results[i][j])])
        absolute_results = [mean_ensemble_distance(values) for values in zip(*results)]
        normalised_results = [mean_ensemble_distance(values) for values in zip(*normalised_results)]
        return min(normalised_results)

    def update(self, static, dynamic, dynamic_changes, base_distance=0, default=None):
        pass

    def mean(self, *args, **kwargs):
        """

        :param prototype: single key of prototype to consider
        :param args:
        :param kwargs:
        :return:
        """
        prototype = kwargs.pop("prototype", 1)
        if len(args) == 1:
            args = args[0]
        if isinstance(args[0], EnsembleSignatureCache):
            tmp = []
            for index, arg in enumerate(args):
                # take caches from ensemble signature cache to create prototype
                for ensemble_idx, signature_cache in enumerate(arg._signature_dicts):
                    # each position is another identity class
                    pc = PrototypeSignatureCache.from_signature_caches(
                            [signature_cache],
                            prototype=prototype[index],
                            threshold=self.threshold)
                    try:
                        tmp[ensemble_idx] += pc
                    except IndexError:
                        tmp.append(pc)
            result = EnsemblePrototypeSignatureCache.from_prototype_signature_caches(cache_list=tmp)
            return result
        else:
            return PrototypeSignatureCache.from_signature_caches(args,
                                                                 prototype=prototype,
                                                                 threshold=self.threshold)

    def median(self, *args, **kwargs):
        return NotImplementedError
