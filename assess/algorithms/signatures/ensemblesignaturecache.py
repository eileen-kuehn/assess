"""
This module implements ensemble version of SignatureCache as well as PrototypeSignatureCache to
enable ensemble based algorithms.
"""
import logging

from assess.algorithms.signatures.signaturecache import SignatureCache, PrototypeSignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class EnsembleSignatureCacheList(list):
    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, list.__repr__(self))


class EnsemblePrototypeSignatureCacheList(list):
    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, list.__repr__(self))


class EnsembleSignatureCache(object):
    """
    The EnsembleSignatureCache holds a list of SignatureCache objects to enable the approach to
    handle different kinds of signatures in parallel.
    """
    def __init__(self, supported=None, statistics_cls=None):
        self._signature_dicts = []
        self.supported = supported or {
            ProcessStartEvent: True,
            ProcessExitEvent: False,
            TrafficEvent: False
        }
        self.statistics_cls = statistics_cls

    def __setitem__(self, key, value):
        signature, event_type = key
        if not self.supported.get(event_type, False):
            logging.getLogger(self.__class__.__name__).warning("Skipping %s (%s) for event %s" % (
                signature, value, event_type))
            return
        for index, token in enumerate(signature):
            try:
                self._signature_dicts[index][token, event_type] = value
            except IndexError:
                self._signature_dicts = [SignatureCache(self.supported, self.statistics_cls)
                                         for _ in range(len(signature))]
                self._signature_dicts[index][token, event_type] = value

    def __iter__(self):
        for signature_dict in self._signature_dicts:
            yield signature_dict

    def get(self, signature):
        """
        Get the current statistics for each signature of a given token. If token does not exist in
        cache, a count of 0 is returned.

        :param signature: Signature to get the count for
        :return: List of current count for tokens, otherwise []
        """
        try:
            return EnsembleSignatureCacheList(
                self._signature_dicts[index].get(signature=token) for index, token in
                enumerate(signature))
        except IndexError:
            return EnsembleSignatureCacheList()

    def multiplicity(self, signature=None, event_type=None, by_event=False):
        """
        Get the current counts for each signature of a given token. If token does not exist in
        cache, a count of 0 is returned.

        If signature is None, the overall multiplicity for a given cache is given

        :param signature: Signature to get the count for
        :return: List of current count for tokens, otherwise []
        """
        try:
            if signature is None:
                return EnsembleSignatureCacheList(cache.multiplicity(
                    event_type=event_type, by_event=by_event) for cache in self._signature_dicts)
            else:
                result = EnsembleSignatureCacheList()
                for index, token in enumerate(signature):
                    result.append(self._signature_dicts[index].multiplicity(
                        signature=token, event_type=event_type, by_event=by_event))
                return result
        except IndexError:
            return EnsembleSignatureCacheList()

    def node_count(self, **kwargs):
        """
        For each signature return the current count of differing tokens in cache.

        :param kwargs:
        :return: List of count of tokens
        """
        return EnsembleSignatureCacheList(
            cache.node_count(**kwargs) for cache in self._signature_dicts)

    def get_statistics(self, signature, key, event_type):
        try:
            return EnsembleSignatureCacheList(
                signature_dict.get_statistics(signature[index], key[index], event_type[index])
                for index, signature_dict in enumerate(self._signature_dicts)
            )
        except IndexError:
            return EnsembleSignatureCacheList()

    def internal(self):
        """
        Method returns list of internal representation of the caches.

        :return: List of signature dicts
        """
        return self._signature_dicts


class EnsemblePrototypeSignatureCache(object):
    """
    The EnsemblePrototypeSignatureCache holds a list of PrototypeSignatureCaches to enable
    ensemble methods for distance measurements.
    """
    def __init__(self, supported=None, statistics_cls=None):
        self._prototype_dict = []
        self.supported = supported or {
            ProcessStartEvent: True,
            ProcessExitEvent: False,
            TrafficEvent: False
        }
        self.statistics_cls = statistics_cls

    def __iter__(self):
        for prototype_dict in self._prototype_dict:
            yield prototype_dict

    def __setitem__(self, key, value):
        signature, prototype, event_type = key
        if not self.supported.get(event_type, False):
            logging.getLogger(self.__class__.__name__).warning("Skipping %s (%s) for event %s" % (
                signature, value, event_type))
            return
        for index, token in enumerate(signature):
            try:
                self._prototype_dict[index][token, prototype, event_type] = value
            except IndexError:
                self._prototype_dict = [PrototypeSignatureCache(
                    self.supported, self.statistics_cls) for _ in range(len(signature))]
                self._prototype_dict[index][token, prototype, event_type] = value

    @classmethod
    def from_prototype_signature_caches(cls, cache_list):
        if cache_list is not None and 0 < len(cache_list):
            result = cls(supported=cache_list[0].supported, statistics_cls=cache_list[0].statistics_cls)
            result._prototype_dict = cache_list
            return result
        return None

    @property
    def signature_cache_count(self):
        return EnsemblePrototypeSignatureCacheList(
            cache.signature_cache_count for cache in self._prototype_dict)

    def node_count(self, prototype=None):
        """
        Returns the list of number of tokens stored for a given prototype.

        Format returned is like this: [p1e1, ..., pnen]

        :param prototype: Prototype to get the number of signatures for
        :return: List of numbers of tokens for prototype
        """
        return EnsemblePrototypeSignatureCacheList(
            cache.node_count(prototype=prototype) for cache in self._prototype_dict)

    def get(self, signature):
        """
        Returns a list of dictionaries of prototypes with their statistics for a given token.
        If the token does not exist, an empty dictionary is returned.

        :param signature: Signature to return the statistics for
        :return: List of dictionaries of prototypes with statistics as value
        """
        try:
            return EnsemblePrototypeSignatureCacheList(
                self._prototype_dict[index].get(signature=token) for index, token in
                enumerate(signature))
        except IndexError:
            return EnsemblePrototypeSignatureCacheList()

    def multiplicity(self, signature=None, prototype=None, event_type=None, by_event=False):
        """
        Returns a list of frequencies of added objects. If no prototype is given, it considers the
        frequency of all elements. Otherwise only the frequency per prototype is given.

        Format returned is like this: [p1e1, ..., p1en]

        :param prototype: Prototype to determine frequency from
        :return: List of frequency of tokens
        """
        if signature is not None:
            return EnsemblePrototypeSignatureCacheList(
                self._prototype_dict[index].multiplicity(
                    signature=token, prototype=prototype, event_type=event_type, by_event=by_event)
                for index, token in enumerate(signature)
            )
        else:
            return EnsemblePrototypeSignatureCacheList(
                prototype_dict.multiplicity(prototype=prototype, event_type=event_type, by_event=by_event)
                for prototype_dict in self._prototype_dict
            )
        return EnsemblePrototypeSignatureCacheList()

    def get_statistics(self, signature, key, event_type, prototype):
        return EnsemblePrototypeSignatureCacheList(
            self._prototype_dict[index].get_statistics(
                signature=token, key=key, event_type=event_type, prototype=prototype)
            for index, token in enumerate(signature)
        )
