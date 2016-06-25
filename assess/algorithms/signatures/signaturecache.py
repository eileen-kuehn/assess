"""
Module contains a general SignatureCache as well as a specialised for prototypes. Currently it
also defines the statistics being available for PrototypeSignatureCache.
"""

from assess.algorithms.statistics.splittedstatistics import SplittedStatistics
from assess.algorithms.statistics.statistics import MeanVariance
from cachemap.frequencycachemap import FrequencyCacheMap


class SignatureCache(object):
    """
    The SignatureCache takes care of managing statistics for based on the signature. Different
    statistics, e.g. MeanVariance can be supported.
    """
    def __init__(self):
        self._prototype_dict = FrequencyCacheMap()

    def add_signature(self, signature=None):
        """
        Adding another occurence of a signature to the current cache. If signature is not in the
        Cache so far, its count is set to 1, otherwise it is incremented.

        :param signature: The signature to be added
        """
        if signature not in self._prototype_dict:
            self._prototype_dict[signature] = 1
        else:
            self._prototype_dict[signature] += 1

    def get(self, signature=None):
        """
        Get the current count for a given signature. If signature does not exist in cache, a count
        of 0 is returned.

        :param signature: Signature to get the count for
        :return: Current count for signature, otherwise 0
        """
        return self._prototype_dict.get(signature, 0)

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
        return sum(self._prototype_dict.values())

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
    def add_signature(self, signature=None, prototype=None, value=0.0):
        """
        Add a signature and its current value for a given prototype.

        :param signature: Signature to add
        :param prototype: Prototype the signature belongs to
        :param value: Value for signature
        """
        prototype_dictionary = self._prototype_dict.setdefault(signature, dict())
        if prototype in prototype_dictionary:
            prototype_dictionary[prototype].add(value=value)
        else:
            statistics = SplittedStatistics(statistics_type=MeanVariance)
            statistics.add(value=value)
            prototype_dictionary[prototype] = statistics

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

    def get(self, signature=None):
        """
        Returns a dictionary of prototypes with their statistics for a given signature. If the
        signature does not exist, an empty dictionary is returned.

        :param signature: Signature to return the statistics for
        :return: Dictionary of prototypes with statistics as value
        """
        return self._prototype_dict.get(signature, dict())

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
                    result += value.get(prototype, None).count
                except AttributeError:
                    pass
        else:
            for value in self._prototype_dict.values():
                for statistics in value.values():
                    result += statistics.count
        return result
