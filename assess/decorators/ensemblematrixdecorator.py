"""
This module offers an implementation to output the different distances for
dynamic trees based on the single events that are processed. The actual output
is in form of a vector.
"""
from assess.decorators.decorator import Decorator
from assess.exceptions.exceptions import MatrixDoesNotMatchBounds


class EnsembleMatrixDecorator(Decorator):
    """
    The EnsembleMatrixDecorator evaluates given distance results from ensembles
    and determines the distance ensemble result.

    Attention: currently ensemble only considers the mean for given signatures!

    The results are given in the following format:
    [                               <- start of matrix
        [                           <- start of a tree
            [p1t1, ..., pnt1]       <- only one ensemble is relevant here
        ],
        ...
        [
            [p1tn, ..., pntn]
        ]
    ]
    """
    def __init__(self, normalized=False):
        if normalized:
            Decorator.__init__(self, name="normalized_ensembles")
        else:
            Decorator.__init__(self, name="ensembles")
        self._data = None
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
        size = self._matrix_size()
        if self._data and size < len(self._data) + 1:
            raise MatrixDoesNotMatchBounds(size, size, len(self._data) + 1)
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()
        # add a new row for a new algorithm for only _one_ ensemble
        self._data.append([[prototype for prototype in self._tmp_prototype_counts[0]]])
        self._last_distance_event = self._tmp_prototype_counts
        # FIXME: self._data.append([prototype for prototype in self._
        # tmp_prototype_counts[0]])

    def _tree_finished(self, result):
        # [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        event_counts = self._algorithm.event_counts()

        i = 0
        for j, prototype_result in enumerate(event_counts[i]):
            if self._normalized:
                distance = self._data[-1][i][j]
                self._data[-1][i][j] = 2 * distance / float(
                    prototype_result + self._tmp_prototype_counts[i][j] + distance)
            else:
                pass

    def _event_added(self, event, result):
        # result looks like [[p1e1, ..., pne1], ..., [p1en, ..., pnen]]
        tmp_differences = [0 for _ in self._algorithm.prototypes]
        # accumulate all differences first
        for i, ensemble_result in enumerate(result):
            for j, prototype_result in enumerate(ensemble_result):
                tmp_differences[j] += prototype_result - self._last_distance_event[i][j]
        # then divide by number of ensembles to get mean
        tmp_differences = [value / float(len(self._tmp_prototype_counts))
                           for value in tmp_differences]
        ensemble_idx = 0
        for index, difference in enumerate(tmp_differences):
            self._data[-1][ensemble_idx][index] += difference
        self._last_distance_event = result

    def _matrix_size(self):
        if self._data is None:
            self._data = [[]]
        if len(self._data) > 0:
            return len(self._algorithm.prototypes)
        return 0

    def _update(self, decorator):
        self._data.extend(decorator.data())

    def __iadd__(self, other):
        """
        [                           [
            [                           [                               tree_idx
                [p1t1e1, p2t1e1],           [p3t1e1, ..., pnt1e1],      ensemble_idx
                ...,                        ...,
                [p1t1en, p2t1en]            [p3t1en, ..., pnt1en]
            ],                          ],
            ...                         ...
            [                           [
                [p1tne1, p2tne1],           [p3tne1, ..., pntne1],
                ...                         ...,
                [p1tnen, p2tnen]            [p3tnen, ..., pntnen]
            ]                           ]
        ]                           ]
        :param other:
        :return:
        """
        try:
            if other.row_idx[0] > self.row_idx[0]:
                # append new trees
                self._data.extend(other._data)
                self.row_idx[0] = other.row_idx[0]
                # as we are starting a new row, we can also take col index
                self.col_idx[0] = other.col_idx[0]
            elif other.row_idx[0] == \
                    self.row_idx[0] and other.col_idx[0] > self.col_idx[0]:
                # append new prototypes
                for tree_idx, tree_values in enumerate(other._data):
                    for ensemble_idx, ensemble_values in enumerate(tree_values):
                        self._data[-(len(other._data) - tree_idx)][ensemble_idx].extend(
                            ensemble_values)
                self.col_idx[0] = other.col_idx[0]
            return self
        except AttributeError:
            pass
        for tree_idx, tree_values in enumerate(other._data):
            for ensemble_idx, ensemble_values in enumerate(tree_values):
                self._data[tree_idx][ensemble_idx].extend(ensemble_values)
        return self
