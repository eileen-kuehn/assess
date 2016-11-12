"""
This module implements ensemble version of SignatureCache as well as PrototypeSignatureCache to
enable ensemble based algorithms.
"""
from assess.algorithms.signatures.signaturecache import SignatureCache, PrototypeSignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class EnsembleSignatureCache(object):
    """
    The EnsembleSignatureCache holds a list of SignatureCache objects to enable the approach to
    handle different kinds of signatures in parallel.
    """
    def __init__(self, supported=None):
        self._signature_dicts = []
        self.supported = supported or {
            ProcessStartEvent: True,
            ProcessExitEvent: False,
            TrafficEvent: False
        }

    def add_signature(self, signature=None, value=None):
        """
        Adding another occurence of a signature to the current cache. If signature is not in the
        Cache so far, its count is set to 1, otherwise it is incremented.

        :param signature: The signature to be added
        """
        for index, token in enumerate(signature):
            try:
                self._signature_dicts[index].add_signature(signature=token, value=value)
            except IndexError:
                self._signature_dicts = [SignatureCache(self.supported) for _ in range(
                    len(signature))]
                self._signature_dicts[index].add_signature(signature=token, value=value)

    def get(self, signature):
        """
        Get the current counts for each signature of a given token. If token does not exist in
        cache, a count of 0 is returned.

        :param signature: Signature to get the count for
        :return: List of current count for tokens, otherwise []
        """
        try:
            return [self._signature_dicts[index].get(signature=token) for index, token in
                    enumerate(signature)]
        except IndexError:
            return []

    def get_count(self, signature):
        """
        Get the current counts for each signature of a given token. If token does not exist in
        cache, a count of 0 is returned.

        :param signature: Signature to get the count for
        :return: List of current count for tokens, otherwise []
        """
        try:
            return [self._signature_dicts[index].get_count(signature=token) for index, token in
                    enumerate(signature)]
        except IndexError:
            return []

    def node_count(self, **kwargs):
        """
        For each signature return the current count of differing tokens in cache.

        :param kwargs:
        :return: List of count of tokens
        """
        return [cache.node_count(**kwargs) for cache in self._signature_dicts]

    def frequency(self):
        """
        Method returns the a list of the overall frequency of all tokens inside the signature
        caches.

        :return: List of accumulated count for all signatures
        """
        return [cache.frequency() for cache in self._signature_dicts]

    def internal(self):
        """
        Method returns list of internal representation of the caches.

        :return: List of signature dicts
        """
        return self._signature_dicts


class EnsemblePrototypeSignatureCache(PrototypeSignatureCache):
    """
    The EnsemblePrototypeSignatureCache holds a list of PrototypeSignatureCaches to enable
    ensemble methods for distance measurements.
    """
    def __init__(self, **kwargs):
        PrototypeSignatureCache.__init__(self, **kwargs)
        self._prototype_dict = []

    def add_signature(self, signature=None, prototype=None, value=None):
        """
        Add a list of tokens and its current values for a given prototype.

        :param signature: List of tokens to add
        :param prototype: Prototype the tokens belong to
        :param value: Value for signatures
        """
        for index, token in enumerate(signature):
            try:
                self._prototype_dict[index].add_signature(signature=token,
                                                          prototype=prototype,
                                                          value=value)
            except IndexError:
                self._prototype_dict = [PrototypeSignatureCache() for _ in range(len(signature))]
                self._prototype_dict[index].add_signature(signature=token,
                                                          prototype=prototype,
                                                          value=value)

    def node_count(self, prototype=None):
        """
        Returns the list of number of tokens stored for a given prototype.

        Format returned is like this: [p1e1, ..., pnen]

        :param prototype: Prototype to get the number of signatures for
        :return: List of numbers of tokens for prototype
        """
        return [cache.node_count(prototype=prototype) for cache in self._prototype_dict]

    def get(self, signature=None):
        """
        Returns a list of dictionaries of prototypes with their statistics for a given token.
        If the token does not exist, an empty dictionary is returned.

        :param signature: Signature to return the statistics for
        :return: List of dictionaries of prototypes with statistics as value
        """
        try:
            return [self._prototype_dict[index].get(signature=token) for index, token in
                    enumerate(signature)]
        except IndexError:
            return []

    def frequency(self, prototype=None):
        """
        Returns a list of frequencies of added objects. If no prototype is given, it considers the
        frequency of all elements. Otherwise only the frequency per prototype is given.

        Format returned is like this: [p1e1, ..., pnen]

        :param prototype: Prototype to determine frequency from
        :return: List of frequency of tokens
        """
        return [cache.frequency(prototype=prototype) for cache in self._prototype_dict]