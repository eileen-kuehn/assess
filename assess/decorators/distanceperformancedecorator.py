"""
This module offers an implementation to determine the performance of distance
calculation. The signature creation process is not measured.
"""

import time
from assess.decorators.decorator import Decorator


class DistancePerformanceDecorator(Decorator):
    """
    The DistancePerformanceDecorator measures the time that is being used to update
    the distance based on single events. Duration for signature creation etc.
    are excluded from this statistic. The Decorator differentiates between
    accumulated and single measurements.

    Format looks like this:
    [
        [v1t1, ..., vnt1],
        ...,
        [v1tn, ..., vntn]]
    ]

    Also for accumulated values, you can expect to have a list in list.
    """
    def __init__(self, accumulated=True):
        if accumulated:
            Decorator.__init__(self, name="accumulated_distance_performance")
        else:
            Decorator.__init__(self, name="distance_performance")
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

    def update_distance(self, event, signature, **kwargs):
        """
        Method that encapsulates the actual call of the update_distance method
        from the algorithm.

        :param event: Event being processed
        :param signature: Signature being processed
        :param kwargs: Additional arguments
        :return: Updated distance
        """
        start = time.time()
        result = self._algorithm.__class__.update_distance(
            self._algorithm,
            event,
            signature,
            **kwargs
        )
        end = time.time()

        self._data[-1].append(end - start)
        return result

    def data(self):
        if self._data:
            if self._accumulated:
                result = [[sum(elem) if len(elem) > 0 else None] for elem in self._data]
                return result
            else:
                return self._data
        return None

    def _update(self, decorator):
        self._data.extend(decorator._data)

    def __iadd__(self, other):
        return NotImplemented
