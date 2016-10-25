"""
This module provides a decorator that takes care to measure performance of signature generation.
"""

import os
from assess.decorators.decorator import Decorator


class SignaturePerformanceDecorator(Decorator):
    """
    The SignaturePerformanceDecorator measures performance for calculation of signatures.
    It differs between accumulated performance as well as single performance measurements.

    Format looks like this:
    {
        "user time": [
            [v1t1, ..., vnt1],
            ...,
            [v1tn, ..., vntn]],
        "system time": [...],
        "children's user time": [...],
        "children's system time": [...],
        "elapsed real time": [...]
    }

    Also for accumulated values, you can expect to have a list in list.
    """
    def __init__(self, accumulated=True):
        if accumulated:
            Decorator.__init__(self, name="accumulated_signature_performance")
        else:
            Decorator.__init__(self, name="signature_performance")
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
            self._performances = {item: [[]] for item in self._items}
        else:
            for item in self._performances.values():
                item.append([])

    def create_signature(self, node, parent):
        """
        This method encapsulates the signature creation process. It measures time from start to
        finish of the process.

        :param node: Node for which the signature is calculated
        :param parent: Parent of node
        :return: Resulting signature
        """
        start = os.times()
        result = self._algorithm.__class__.create_signature(self._algorithm, node, parent)
        end = os.times()

        for index, start_value in enumerate(start):
            self._performances[self._items[index]][-1].append(end[index] - start_value)
        return result

    def data(self):
        if self._performances:
            if self._accumulated:
                result = {item: [[]] for item in self._items}
                for key in self._performances.keys():
                    if len(self._performances[key][0]) > 0:
                        result[key] = [[sum(elements)] for elements in self._performances[key]]
                    else:
                        result[key] = [[]]
                return result
            else:
                return self._performances
        return None

    def _update(self, decorator):
        for key in self._performances.keys():
            if self._accumulated:
                self._performances[key] = self._performances[key] + decorator.data()[key]
            else:
                self._performances[key].extend(decorator.data()[key])
