"""
This module provides a decorator implementation for getting the overall
performance regarding the distance measurement process as well as the signature
creation process.
"""

import time

from assess.decorators.decorator import Decorator


class PerformanceDecorator(Decorator):
    """
    The PerformanceDecorator measures the time from start to end of processing
    of a single event.

    Format looks like this:
    [
        [v1t1, ..., vnt1],
        ...,
        [v1tn, ..., vntn]]
    ]

    Also for accumulated values, you can expect to have a list in list.
    """
    __slots__ = ("_data", "_start", "_accumulated")

    def __init__(self, accumulated=True):
        if accumulated:
            Decorator.__init__(self, name="accumulated_performance")
        else:
            Decorator.__init__(self, name="performance")
        self._data = None
        self._start = None
        self._accumulated = accumulated

    def _algorithm_updated(self):
        self._data = None
        self._start = None

    def _tree_started(self):
        if self._data is None:
            self._data = [[]]
        else:
            self._data.append([])

    def _event_will_be_added(self):
        self._start = time.time()

    def _event_added(self, event, result):
        if event is None:
            return
        end = time.time()
        try:
            self._data[-1].append(end - self._start)
        except TypeError:
            # for result lists there is no start, because it has already
            # been processed, so set 0
            self._data[-1].append(0)
        self._start = None

    def data(self):
        if self._data:
            if self._accumulated:
                result = [[sum(elem) if len(elem) > 0 else None]
                          for elem in self._data]
                return result
            else:
                return self._data
        return None

    def _update(self, decorator):
        self._data.extend(decorator._data)

    def __iadd__(self, other):
        return NotImplemented
