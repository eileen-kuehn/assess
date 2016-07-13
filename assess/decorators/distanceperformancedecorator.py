"""
This module offers an implementation to determine the performance of distance calculation.
The signature creation process is not measured.
"""

import os
from assess.decorators.decorator import Decorator


class DistancePerformanceDecorator(Decorator):
    """
    The DistancePerofrmanceDecorator measures the time that is being used to update the distance
    based on single events. Duration for signature creation etc. are excluded from this statistic.
    The Decorator differentiates between accumulated and single measurements.
    """
    def __init__(self, accumulated=True):
        if accumulated:
            Decorator.__init__(self, name="accumulated_distance_performance")
        else:
            Decorator.__init__(self, name="distance_performance")
        self._items = ["user time", "system time", "children's user time", "children's system time",
                       "elapsed real time"]
        self._performances = None
        self._start = None
        self._accumulated = accumulated

    def _algorithm_updated(self):
        self._performances = None
        self._start = None

    def _tree_started(self):
        if self._performances is None:
            self._performances = [{}]
        else:
            self._performances.append({})

    def update_distance(self, event, signature, **kwargs):
        """
        Method that encapsulates the actual call of the update_distance method from the algorithm.

        :param event: Event being processed
        :param signature: Signature being processed
        :param kwargs: Additional arguments
        :return: Updated distance
        """
        start = os.times()
        result = self._algorithm.__class__.update_distance(
            self._algorithm,
            event,
            signature,
            **kwargs
        )
        end = os.times()
        result_dict = zip(self._items, [end[i] - start[i] for i in range(len(start))])
        for key, value in result_dict:
            self._performances[-1].setdefault(key, []).append(value)
        return result

    def data(self):
        if self._performances is not None:
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
        return None

    def _update(self, decorator):
        self._performances.extend(decorator.data())

    def _compatible(self, decorator):
        return type(decorator) == type(self) and self._accumulated == decorator._accumulated
