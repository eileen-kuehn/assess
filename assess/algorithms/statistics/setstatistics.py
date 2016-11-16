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
    def __init__(self):
        self._data = collections.Counter()

    def __add__(self, other):
        result = type(self._data)()
        return result.update(other._data)

    def __iadd__(self, other):
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

    def distance(self, value):
        if value is None:
            return None
        if self._convert(value) in self._data:
            return 0
        return 1

    def _convert(self, value):
        return int(round(math.sqrt(value)))

    def _unconvert(self, value):
        return value**2
