"""
This module provides a decorator that takes care to measure performance of signature generation.
"""

import os
from assess.decorators.decorator import Decorator


class SignaturePerformanceDecorator(Decorator):
    """
    The SignaturePerformanceDecorator measures performance for calculation of signatures.
    It differs between accumulated performance as well as single performance measurements.
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
            self._performances = [{}]
        else:
            self._performances.append({})

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
