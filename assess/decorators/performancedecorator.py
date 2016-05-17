"""
This module provides a decorator implementation for getting the overall performance regarding
the distance measurement process as well as the signature creation process.
"""

import os

from assess.decorators.decorator import Decorator


class PerformanceDecorator(Decorator):
    """
    The PerformanceDecorator measures the time from start to end of processing of a single event.
    """
    def __init__(self, accumulated=True):
        if accumulated:
            Decorator.__init__(self, name="accumulated_performance")
        else:
            Decorator.__init__(self, name="performance")
        self._items = ["user time", "system time", "children's user time", "children's system time",
                       "elapsed real time"]
        self._performances = []
        self._start = None
        self._accumulated = accumulated

    def _algorithm_updated(self):
        self._performances = []
        self._start = None

    def _tree_started(self):
        self._performances.append({})

    def _event_will_be_added(self):
        self._start = os.times()

    def _event_added(self, event, result):
        if event is None:
            return
        end = os.times()
        result_dict = zip(self._items, [end[i] - self._start[i] for i in range(len(self._start))])
        self._start = None
        for key, value in result_dict:
            self._performances[-1].setdefault(key, []).append(value)

    def data(self):
        if self._accumulated:
            result = []
            for performance in self._performances:
                result.append({})
                for key in performance:
                    try:
                        result[-1][key] = sum(performance[key])
                    except TypeError:
                        result[-1][key] = performance[key]
            return result
        else:
            return self._performances

