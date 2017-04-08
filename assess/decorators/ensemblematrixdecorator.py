"""
This module offers an implementation to output the different distances for dynamic trees based
on the single events that are processed. The actual output is in form of a vector.
"""

from assess.decorators.decorator import Decorator


class EnsembleMatrixDecorator(Decorator):
    """
    The EnsembleMatrixDecorator evaluates given distance results from ensembles and determines
    the distance ensemble result.

    Attention: currently ensemble only considers the mean for given signatures!

    The results are given in the following format:
    [                               <- start of matrix
        [p1t1, ..., pnt1]           <- list of distance events per prototype considering all ensembles
        ...
        [p1tn, ..., pntn]
    ]
    """
    def __init__(self, normalized=False):
        if normalized:
            Decorator.__init__(self, name="normalized_ensembles")
        else:
            Decorator.__init__(self, name="ensembles")
        self._data = []
        self._normalized = normalized
        # format: [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        self._tmp_prototype_counts = None
        self._last_distance_event = None

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._tmp_prototype_counts = None

    def _tree_started(self):
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()
        self._last_distance_event = self._tmp_prototype_counts
        self._data.append([prototype for prototype in self._tmp_prototype_counts[0]])

    def _tree_finished(self, result):
        event_counts = self._algorithm.event_counts()  # [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        for j, prototype_result in enumerate(event_counts[0]):
            if self._normalized:
                distance = self._data[-1][j]
                self._data[-1][j] = 2 * distance / float(
                    event_counts[0][j] + self._tmp_prototype_counts[0][j] + distance)
            else:
                pass

    def _event_added(self, event, result):
        # result looks like [[p1e1, ..., pne1], ..., [p1en, ..., pnen]]
        event_counts = self._algorithm.event_counts()  # [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        # check if we have equal number of events for different ensembles
        # FIXME: removed assertion for equal count of events
        # assert 1 in set([len(set(elem)) for elem in zip(*event_counts)])

        tmp_differences = [0 for _ in self._algorithm.prototypes]
        # accumulate all differences first
        for i, ensemble_result in enumerate(result):
            for j, prototype_result in enumerate(ensemble_result):
                tmp_differences[j] += result[i][j] - self._last_distance_event[i][j]
        # then divide by number of ensembles to get mean
        tmp_differences = [value / float(len(self._tmp_prototype_counts)) for value in tmp_differences]
        for index, difference in enumerate(tmp_differences):
            self._data[-1][index] += difference
        self._last_distance_event = result

    def _update(self, decorator):
        self._data.extend(decorator.data())

    def __iadd__(self, other):
        for tree_idx, tree_values in enumerate(other._data):
            self._data[tree_idx].extend(tree_values)
        return self
