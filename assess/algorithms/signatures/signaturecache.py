import math

from cachemap.frequencycachemap import FrequencyCacheMap


class SignatureCache(object):
    def __init__(self):
        self._prototype_dict = FrequencyCacheMap()

    def add_signature(self, signature=None):
        if signature not in self._prototype_dict:
            self._prototype_dict[signature] = 1
        else:
            self._prototype_dict[signature] += 1

    def get(self, signature=None, **kwargs):
        return self._prototype_dict.get(signature, 0)

    def node_count(self, **kwargs):
        return len(self._prototype_dict.keys())

    def frequency(self, **kwargs):
        return sum(self._prototype_dict.values())

    def internal(self):
        return self._prototype_dict


# TODO: move it somewhere
class MeanVariance(object):
        def __init__(self, value=0.0):
            self._count = 1 if value != 0 else 0
            self._overall_count = 1
            self._mean = value
            self._variance = 0.0
            # remember for faster calculation
            self._first_part = None
            self._second_part = None

        def add(self, value=0.0):
            self._overall_count += 1
            if value != 0:
                self._count += 1
                new_mean = self._mean + (value - self._mean) / self._count
                self._variance += (value - self._mean) * (value - new_mean)
                self._mean = new_mean

        def first_part(self):
            """
            curve(a*exp(-b*x*x), -3, 3)
            :return:
            """
            return 1
            # if self._first_part is None:
            #     try:
            #         self._first_part = 1 / (math.sqrt(2*math.pi*self._variance))
            #     except ZeroDivisionError:
            #         self._first_part = 0
            # return self._first_part

        def second_part(self):
            if self._second_part is None:
                try:
                    self._second_part = -1 / (2*self._variance)
                except ZeroDivisionError:
                    self._second_part = 0
            return self._second_part

        def distance(self, value=None):
            if value is None or value == 0:
                return None
            return self.first_part() * math.exp(self.second_part()*(value-self._mean)**2)

        @property
        def count(self):
            return self._overall_count


class PrototypeSignatureCache(SignatureCache):
    def add_signature(self, signature=None, prototype=None, value=0.0):
        prototype_dictionary = self._prototype_dict.setdefault(signature, dict())
        if prototype in prototype_dictionary:
            prototype_dictionary[prototype].add(value=value)
        else:
            prototype_dictionary[prototype] = MeanVariance(value=value)

    def node_count(self, prototype=None):
        # TODO: maybe work with a filter here
        if prototype is None:
            return len(self._prototype_dict)
        count = 0
        for values in self._prototype_dict.values():
            for value in values:
                if value == prototype:
                    count += 1
        return count

    def get(self, signature=None, **kwargs):
        return self._prototype_dict.get(signature, dict())
