import math
import collections

from assess.algorithms.statistics.statistics import Statistic, Statistics


class SetStatistic(Statistic):
    def __init__(self, value, count):
        self._count = count
        self._value = value

    @property
    def count(self):
        return self._count

    @property
    def value(self):
        return self._value


class SetStatistics(Statistics):
    def __init__(self, convert=lambda value: int(round(math.sqrt(value))),
                 unconvert=lambda value: value**2):
        self._data = collections.Counter()
        self._convert = convert
        self._unconvert = unconvert

    def __add__(self, other):
        result = type(self)(convert=self._convert, unconvert=self._unconvert)
        result._data.update(self._data)
        if other is not None:
            result._data.update(other._data)
        return result

    def __iadd__(self, other):
        if other is not None:
            self._data.update(other._data)
        return self

    def __iter__(self):
        for key, count in self._data.items():
            statistic = SetStatistic(self._unconvert(key), count)
            yield statistic

    def add(self, value):
        self._data.update([self._convert(value)])

    def count(self, value=None):
        if value is not None:
            converted = self._convert(value)
            return self._data.get(converted, 0)
        return sum(self._data.values())

    def distance(self, value, count=0):
        if value is None:
            return None
        converted = self._convert(value)
        if converted in self._data:
            # also ensure count
            if count < self._data.get(converted, 0):
                return 0
        return 1

    @classmethod
    def mean(cls, values, length=None):
        result = sum(values[1:], values[0])
        for key in result._data:
            result._data[key] /= float(len(values) if length is None else length)
        return result

    def __repr__(self):
        values = [(key, value) for key, value in self._data.items()]
        if len(values) > 3:
            return "%s: %s..." % (self.__class__.__name__, values[0:3])
        return "%s: %s" % (self.__class__.__name__, values)
