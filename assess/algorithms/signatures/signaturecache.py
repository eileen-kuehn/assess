"""
Module contains a general SignatureCache as well as a specialised for prototypes. Currently it
also defines the statistics being available for PrototypeSignatureCache.
"""
import logging

from assess.algorithms.statistics.splittedstatistics import SplittedStatistics
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class SignatureCache(object):
    """
    The SignatureCache takes care of managing statistics for based on the signature. Different
    statistics, e.g. MeanVariance can be supported.
    """
    def __init__(self, supported=None, statistics_cls=None):
        self._prototype_dict = {}
        self.supported = supported or {
            ProcessStartEvent: True,
            ProcessExitEvent: False,
            TrafficEvent: False
        }
        self._keys = None
        self.statistics_cls = statistics_cls or SplittedStatistics

    def __setitem__(self, key, value):
        signature, event_type = key
        if not self.supported.get(event_type, False):
            logging.getLogger(self.__class__.__name__).warning("Skipping %s (%s) for event %s" % (
                signature, value, event_type))
            return
        current_value = self._prototype_dict.setdefault(signature, {}).setdefault(event_type, {})
        for key in value:
            current_value.setdefault(key, self.statistics_cls()).add(value[key])

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

    def support_keys(self):
        if self._keys is None:
            self._keys = []
            for key, value in self.supported.items():
                if value:
                    self._keys.append(key)
        return self._keys

    def get(self, signature):
        """
        Get the current internal statistics for given signature

        :param signature: Signature to get the count for
        :return: Current statistics for signature
        """
        return self[signature]

    def get_statistics(self, signature, key, event_type):
        return self._prototype_dict.get(signature, {}).get(event_type, {}).get(key, self.statistics_cls())

    def node_count(self, **kwargs):
        """
        Return the current count of differing signatures in cache.

        :param kwargs:
        :return: Count of signatures
        """
        return len(self._prototype_dict.keys())

    def _count_for_statistics(self, statistics, event_type):
        result = 0
        if event_type is None:
            # iterate over all supported keys
            for support_key in self.support_keys():
                result += statistics.get(support_key, {}).get("count", self.statistics_cls()).count()
        else:
            result += statistics.get(event_type, {}).get("count", self.statistics_cls()).count()
        return result

    def multiplicity(self, signature=None, event_type=None, by_event=False):
        """
        Method returns the overall multiplicity of all signatures inside the cache, either for a
        given event_type or for all available keys.

        :param event_type: The event_type to consider for determining frequency
        :return: Accumulated count for all signatures
        """
        if by_event and event_type is None:
            result = {}
            for event_key in self.support_keys():
                current_result = 0
                for statistics in self._prototype_dict.values():
                    current_result += self._count_for_statistics(statistics, event_key)
                result[event_key] = current_result
        else:
            result = 0
            if signature is None:
                for statistics in self._prototype_dict.values():
                    result += self._count_for_statistics(statistics, event_type)
            else:
                result += self._count_for_statistics(self._prototype_dict.get(signature, {}), event_type)
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

    def __setitem__(self, key, value):
        signature, prototype, event_type = key
        if not self.supported.get(event_type, False):
            logging.getLogger(self.__class__.__name__).warning("Skipping %s (%s) for event %s" % (
                signature, value, event_type))
            return
        if signature is not None:
            prototype_dictionary = self._prototype_dict.setdefault(signature, dict())
            current_value = prototype_dictionary.setdefault(prototype, {}).setdefault(event_type, {})
            for item in value:
                current_value.setdefault(item, self.statistics_cls()).add(value=value[item])

    def __iadd__(self, other):
        if type(self) != type(other):
            return NotImplemented
        if self.supported != other.supported:
            return NotImplemented
        if self.statistics_cls != other.statistics_cls:
            return NotImplemented
        for signature in other:
            other_dict = other[signature]
            for prototype, values in other_dict.items():
                if self.multiplicity(signature, prototype) > 0:
                    logging.getLogger(self.__class__.__name__).warning(
                        "skipping signature %s for prototype %s because it already exists" % (signature, prototype))
                    continue
                for event_type, statistics in values.items():
                    try:
                        for stat_key, statistic in statistics.items():
                            current = self._prototype_dict.setdefault(signature, {}).setdefault(prototype, {}).setdefault(event_type, {}).setdefault(stat_key, self.statistics_cls())
                            current += statistic
                    except AttributeError:
                        current = self._prototype_dict.setdefault(signature, {}).setdefault(prototype, {})
                        current[event_type] = statistics
        return self

    @classmethod
    def from_signature_caches(cls, signature_caches, prototype=None, threshold=.1):
        """
        Method combines several usual signature cache objects to one single prototype signature
        cache object by taking the somehow defined average.

        :param signature_caches: List of signature caches to consider
        :param prototype: Reference of prototype to consider for resulting cache
        :param threshold: Threshold to consider for dropping signatures
        :return:
        """
        # FIXME: how can I ensure that event statistics stays stable when dropping thresholds?
        result = cls(supported=signature_caches[0].supported, statistics_cls=signature_caches[0].statistics_cls)
        # FIXME: I should maybe also consider that a prototype can be part of a new prototype?
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
                collected = {}  # {supported_key: {statistics_key: [...]}}
                for signature_cache in signature_caches:
                    signatures = signature_cache.get(signature=token)
                    if signatures is not None:
                        for supported_key, statistics in signatures.items():
                            for statistics_key, value in statistics.items():
                                collected.setdefault(supported_key, {}).setdefault(statistics_key, []).append(value)
                prototype_dictionary = result._prototype_dict.setdefault(token, {})
                current_value = prototype_dictionary.setdefault(prototype, {})
                for event_type, statistics in collected.items():
                    for statistics_key, statistic_list in statistics.items():
                        current_value.setdefault(event_type, {})[statistics_key] = \
                            statistic_list[0].mean(statistic_list, length=len(signature_caches))
                current_value["probability"] = probability
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
        signature_cache = cls(supported={object: True})
        for cluster in cluster_representatives.keys():
            for element in cluster_representatives[cluster]:
                signature_cache[element["name"], cluster, object] = None
        return signature_cache

    def add_signature(self, signature, prototype=None, value=None):
        """
        Add a signature and its current value for a given prototype.

        :param signature: Signature to add
        :param prototype: Prototype the signature belongs to
        :param value: Value for signature
        """
        raise NotImplementedError

    def node_count(self, prototype=None):
        """
        Returns the number of signatures stored for a given prototype.

        :param prototype: Prototype to get the number of signatures for
        :return: Number of signature for prototype
        """
        if prototype is None:
            return len(self._prototype_dict)
        return sum([1 for value in self._prototype_dict.values() if prototype in value])

    def __getitem__(self, item):
        return self._prototype_dict.get(item, dict())

    def get_statistics(self, signature, key, event_type, prototype):
        return self._prototype_dict.get(signature, {}).get(prototype, {}).get(event_type, {}).get(key, self.statistics_cls())

    def get(self, signature):
        """
        Returns a dictionary of prototypes with their statistics for a given signature. If the
        signature does not exist, an empty dictionary is returned.

        :param signature: Signature to return the statistics for
        :return: Dictionary of prototypes with statistics as value
        """
        return self[signature]

    def multiplicity(self, signature=None, prototype=None, event_type=None, by_event=False):
        """
        Returns the frequency of added objects. If no prototype is given, it considers the frequency
        of all elements. Otherwise only the frequency per prototype is given.
        This can further be detailed by specifying signature or event_type.

        :param signature: Signature to determine frequency from
        :param prototype: Prototype to determine frequency from
        :param event_type: Event_type to determine frequency from
        :return: Frequency of signatures
        """
        result = 0
        if prototype is not None:
            if by_event and event_type is None:
                result = {}
                for event_key in self.support_keys():
                    current_result = 0
                    for signatures in self._prototype_dict.values():
                        current_result += self._count_for_statistics(signatures.get(prototype, {}), event_key)
                    result[event_key] = current_result
            else:
                if signature is None:
                    for signatures in self._prototype_dict.values():
                        result += self._count_for_statistics(signatures.get(prototype, {}), event_type)
                else:
                    current_dict = self._prototype_dict.get(signature, {})
                    result += self._count_for_statistics(current_dict.get(prototype, {}), event_type)
        else:
            if by_event and event_type is None:
                raise NotImplementedError
            if signature is None:
                for prototype_dict in self._prototype_dict.values():
                    for statistics in prototype_dict.values():
                        result += self._count_for_statistics(statistics, event_type)
            else:
                current_dict = self._prototype_dict.get(signature, {})
                for statistics in current_dict.values():
                    result += self._count_for_statistics(statistics, event_type)
        return result
