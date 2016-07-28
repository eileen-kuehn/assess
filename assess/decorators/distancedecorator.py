"""
This module offers an implementation to output the different distances for dynamic trees based
on the single events that are processed. The actual output is in form of a vector.
"""

from assess.decorators.decorator import Decorator


class DistanceDecorator(Decorator):
    """
    The DistanceDecorator takes care to initialize a vector of distances. For each event the current
    distance is given. The class also differentiates between normalized and not normalized results.
    """
    def __init__(self, normalized=False):
        if normalized:
            Decorator.__init__(self, name="normalized_distances")
        else:
            Decorator.__init__(self, name="distances")
        self._distances = []
        self._normalized = normalized
        self._tmp_prototype_counts = None

    def data(self):
        return self._distances

    def _algorithm_updated(self):
        self._distances = []
        self._tmp_prototype_counts = None

    def _tree_started(self):
        self._distances.append([[] for _ in self._algorithm.prototypes])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()

    def _event_added(self, event, result):
        event_counts = self._algorithm.event_counts()
        for i, _ in enumerate(result):
            if self._normalized:
                self._distances[-1][i].append(result[i] /
                                              float(event_counts[i]+self._tmp_prototype_counts[i]))
            else:
                self._distances[-1][i].append(result[i])

    def _update(self, decorator):
        self._distances.extend(decorator.data())
