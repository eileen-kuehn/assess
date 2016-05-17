"""
Module contains a general SignatureCache as well as a specialised for prototypes. Currently it
also defines the statistics being available for PrototypeSignatureCache.
"""
import math

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


# TODO: move it somewhere
class MeanVariance(object):
    """
    Supported kind of statistic that can be utilised in SignatureCache to store signatures.
    The MeanVariance class offers a running mean and variance for inserted signatures and their
    assigned values.
    """
    def __init__(self, value=0.0):
        self._count = 1 if value != 0 else 0
        self._overall_count = 1
        self._mean = value
        self._variance = 0.0
        # remember for faster calculation
        self._first_part = None
        self._second_part = None

    def add(self, value=0.0):
        """
        Method to add a specific value for a given signature to its cache value.
        :param value: New value to add
        """
        self._overall_count += 1
        if value != 0:
            self._count += 1
            new_mean = self._mean + (value - self._mean) / self._count
            self._variance += (value - self._mean) * (value - new_mean)
            self._mean = new_mean

    @staticmethod
    def _get_first_part():
        """
        Internal method that allows caching for first part of probability distribution function.
        Currently the value is just a static one to directly map to a distance. 1 means, it is
        equal, 0 means it has a very far distance.
        curve(a*exp(-b*x*x), -3, 3)
        :return: First part of pdf
        """
        return 1
        # if self._first_part is None:
        #     try:
        #         self._first_part = 1 / (math.sqrt(2*math.pi*self._variance))
        #     except ZeroDivisionError:
        #         self._first_part = 0
        # return self._first_part

    def _get_second_part(self):
        """
        Internal method that allows caching for second part of probability distribution function.
        If the value has already been calculated before, the cached value is returned, otherwise
        the value is initialised first.
        :return: Second part of pdf
        """
        if self._second_part is None:
            try:
                self._second_part = -1 / (2*self._variance)
            except ZeroDivisionError:
                self._second_part = 0
        return self._second_part

    def distance(self, value=None):
        """
        Check the current distance for a given value. The distance is not a distance in this way but
        more a similarity. If the value equals the mean, 1 is returned. For convenience, value being
        None or 0 get a distance of None, meaning, that the handling can be done externally.

        :param value: The value to check the distance for
        :return: Distance (interpreted in the sense of similarity)
        """
        if value is None or value == 0:
            return None
        return self._get_first_part() * math.exp(self._get_second_part()*(value-self._mean)**2)

    @property
    def count(self):
        """
        Get the number of values that went into the statistics calculation.

        :return: Count of considered values
        """
        return self._overall_count


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
            prototype_dictionary[prototype] = MeanVariance(value=value)

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
