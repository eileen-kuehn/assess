"""
This module provides a decorator that takes care to measure performance of signature generation.
"""

import time
from assess.decorators.decorator import Decorator


class SignaturePerformanceDecorator(Decorator):
    """
    The SignaturePerformanceDecorator measures performance for calculation of signatures.
    It differs between accumulated performance as well as single performance measurements.

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
            Decorator.__init__(self, name="accumulated_signature_performance")
        else:
            Decorator.__init__(self, name="signature_performance")
        self._data = None
        self._accumulated = accumulated

    def _algorithm_updated(self):
        self._data = None
        self._start = None

    def _tree_started(self):
        if self._data is None:
            self._data = [[]]
        else:
            self._data.append([])

    def create_signature(self, node, parent):
        """
        This method encapsulates the signature creation process. It measures time from start to
        finish of the process.

        :param node: Node for which the signature is calculated
        :param parent: Parent of node
        :return: Resulting signature
        """
        start = time.time()
        result = self._algorithm.__class__.create_signature(self._algorithm, node, parent)
        end = time.time()

        self._data[-1].append(end - start)
        return result

    def create_signature_for_finished_node(self, node):
        """
        This method encapsulates the signature creation process for nodes that are finished.
        Thus those signature that need to be appended at the end of sibling lists.

        :param node:
        :return:
        """
        start = time.time()
        result = self._algorithm.__class__.create_signature_for_finished_node(self._algorithm, node)
        end = time.time()

        self._data[-1].append(end-start)
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
