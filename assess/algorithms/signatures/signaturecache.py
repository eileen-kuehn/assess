"""
Module contains a general SignatureCache as well as a specialised for prototypes. Currently it
also defines the statistics being available for PrototypeSignatureCache.
"""

from assess.algorithms.statistics.splittedstatistics import SplittedStatistics
from assess.algorithms.statistics.statistics import MeanVariance
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from cachemap.frequencycachemap import FrequencyCacheMap


class SignatureCache(object):
    """
    The SignatureCache takes care of managing statistics for based on the signature. Different
    statistics, e.g. MeanVariance can be supported.
    """
    def __init__(self, supported=None, statistics_cls=None):
        self._prototype_dict = FrequencyCacheMap()
        self.supported = supported or {
            ProcessStartEvent: True,
            ProcessExitEvent: False,
            TrafficEvent: False
        }
        self.statistics_cls = statistics_cls or SplittedStatistics

    def __setitem__(self, key, value):
        try:
            self._prototype_dict[key] = value
        except KeyError:
            self._prototype_dict[key] = value

    def __getitem__(self, item):
        return self._prototype_dict.get(item, None)

    def __iter__(self):
        for signature in self._prototype_dict:
            yield signature

    def __contains__(self, item):
        if item in self._prototype_dict:
            return True
        return False

    def __len__(self):
        return len(self._prototype_dict.keys())

    def add_signature(self, signature=None, value=None):
        """
        Adding another occurence of a signature to the current cache. If signature is not in the
        Cache so far, its count is set to 1, otherwise it is incremented.

        :param signature: The signature to be added
        :param value: The value to be added to the current signature cache
        """
        current_value = self._prototype_dict.get(signature, {})
        if value:
            for key in value:
                current_value.setdefault(key, self.statistics_cls()).add(value[key])
        try:
            current_value["count"] += 1
        except KeyError:
            current_value["count"] = 1
        self[signature] = current_value

    def get(self, signature):
        """
        Get the current value for given signature

        :param signature: Signature to get the count for
        :return: Current count for signature, otherwise 0
        """
        return self[signature]

    def get_count(self, signature):
        """
        Get the current count for a given signature. If signature does not exist in cache, a count
        of 0 is returned.

        :param signature: Signature to get the count for
        :return: Current count for signature, otherwise 0
        """
        try:
            return self._prototype_dict.get(signature, {}).get("count", 0)
        except KeyError:
            return 0

    def get_statistics(self, signature, key):
        pass

    def node_count(self, **kwargs):
        """
        Return the current count of differing signatures in cache.

        :param kwargs:
        :return: Count of signatures
        """
        return len(self._prototype_dict.keys())

    def frequency(self):
        """
        Method returns the overall frequency of all signatures inside the cache.

        :return: Accumulated count for all signatures
        """
        result = 0
        for _, _, score in self._prototype_dict.iterscoreditems():
            result += score
        return result

    def internal(self):
        """
        Method returns internal representation of the cache.

        :return: Dict of signatures
        """
        return self._prototype_dict


class PrototypeSignatureCache(SignatureCache):
    """
    The PrototypeSignatureCache offers a specialised SignatureCache for Prototypes. It does not only
    do a count on signatures but also introduces a MeanVariance statistic on a given value for
    signatures.
    """
    def __init__(self, supported=None, statistics_cls=None):
        self.signature_cache_count = 1
        SignatureCache.__init__(self, supported=supported, statistics_cls=statistics_cls)

    def __iadd__(self, other):
        if self.supported != other.supported:
            return NotImplemented
        if self.statistics_cls != other.statistics_cls:
            return NotImplemented
        for signature in other.internal().keys():
            other_dict = other[signature]
            for key in other_dict.keys():
                try:
                    for statistic in other_dict[key]["duration"]:
                        for _ in range(statistic.count):
                            self.add_signature(signature=signature,
                                               prototype=key,
                                               value={"duration": statistic.value})
                    current_count = other_dict[key]["duration"].count()
                except KeyError:
                    current_count = 0
                for _ in range(other_dict[key]["count"]-current_count):
                    self.add_signature(signature=signature, prototype=key)
        return self

    @classmethod
    def from_signature_caches(cls, signature_caches, prototype=None, threshold=.1):
        result = cls(signature_caches[0].supported)
        result.signature_cache_count = len(signature_caches)
        token_set = set()
        for signature_cache in signature_caches:
            token_set.update(signature_cache.internal().keys())
        for token in token_set:
            occurences = len([1 for signature_cache in signature_caches
                              if token in signature_cache])
            probability = occurences / float(len(signature_caches))
            if probability > threshold:
                # signature is getting part of prototype signature
                # calculate average count
                counts = sum([signature_cache.get_count(token) for
                              signature_cache in signature_caches])
                durations = [signature_cache[token]["duration"] for
                             signature_cache in signature_caches if token in signature_cache]
                prototype_dictionary = result._prototype_dict.get(token, dict())
                current_value = prototype_dictionary.setdefault(prototype, {})
                current_value["duration"] = type(durations[0]).mean(durations)
                current_value["count"] = int(round(counts / float(len(signature_caches))))
                current_value["probability"] = probability
                result[token] = prototype_dictionary
        return result

    @classmethod
    def from_cluster_representatives(cls, cluster_representatives):
        """
        Method builds a PrototypeSignatureCache by a given dict describing Cluster Representatives
        that are currently calculated from R.
        The current format follows the given convention:
            {"cluster_name":
                [
                    {"name": <name>, "p": <probability>},
                    ...
                ], ...
            }

        :param cluster_representatives: dict of cluster representatives
        :return: valid PrototypeSignatureCache object
        """
        signature_cache = cls()
        for cluster in cluster_representatives.keys():
            for element in cluster_representatives[cluster]:
                # TODO: what about given probabilities? Can they be integrated?
                signature_cache.add_signature(signature=element["name"], prototype=cluster)
        return signature_cache

    def add_signature(self, signature, prototype=None, value=None):
        """
        Add a signature and its current value for a given prototype.

        :param signature: Signature to add
        :param prototype: Prototype the signature belongs to
        :param value: Value for signature
        """
        if signature is not None:
            prototype_dictionary = self._prototype_dict.get(signature, dict())
            current_value = prototype_dictionary.setdefault(prototype, {})
            if value:
                for key in value:
                    current_value.setdefault(key, self.statistics_cls()).add(value=value[key])
            try:
                current_value["count"] += 1
            except KeyError:
                current_value["count"] = 1
            # bumps the current count and sets current values
            self._prototype_dict[signature] = prototype_dictionary

    def node_count(self, prototype=None):
        """
        Returns the number of signatures stored for a given prototype.

        :param prototype: Prototype to get the number of signatures for
        :return: Number of signature for prototype
        """
        # TODO: maybe work with a filter here
        if prototype is None:
            return len(self._prototype_dict)
        count = 0
        for values in self._prototype_dict.values():
            for value in values:
                if value == prototype:
                    count += 1
        return count

    def __getitem__(self, item):
        return self._prototype_dict.get(item, dict())

    def get_count(self, signature, prototype):
        """
        Get the current count for a given signature. If signature does not exist in cache, a count
        of 0 is returned.

        :param signature: Signature to get the count for
        :return: Current count for signature, otherwise 0
        """
        try:
            return self._prototype_dict.get(signature, {}).get(prototype, {}).get("count", 0)
        except KeyError:
            return 0

    def get(self, signature):
        """
        Returns a dictionary of prototypes with their statistics for a given signature. If the
        signature does not exist, an empty dictionary is returned.

        :param signature: Signature to return the statistics for
        :return: Dictionary of prototypes with statistics as value
        """
        return self[signature]

    def frequency(self, prototype=None):
        """
        Returns the frequency of added objects. If no prototype is given, it considers the frequency
        of all elements. Otherwise only the frequency per prototype is given.

        :param prototype: Prototype to determine frequency from
        :return: Frequency of signatures
        """
        result = 0
        if prototype is not None:
            for value in self._prototype_dict.values():
                try:
                    result += value.get(prototype, {})["count"]
                except KeyError:
                    pass
        else:
            for prototype_dict in self._prototype_dict.values():
                for value_dict in prototype_dict.values():
                    result += value_dict.get("count", 0)
        return result
