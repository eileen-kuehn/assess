import math
import collections

from assess.algorithms.statistics.statistics import Statistics


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
        for item in self._data:
            yield item

    def add(self, value):
        self._data.update([self._convert(value)])

    @property
    def count(self):
        return sum(self._data.values())

    def distance(self, value):
        if self._convert(value) in self._data:
            return 0
        return 1

    def _convert(self, value):
        return int(round(math.sqrt(value)))
