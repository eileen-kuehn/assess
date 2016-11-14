"""
This module offers an implementation to generate the distance matrix for given dynamic trees.
"""

from assess.decorators.decorator import Decorator
from assess.exceptions.exceptions import MatrixDoesNotMatchBounds


class DistanceMatrixDecorator(Decorator):
    """
    The DistanceMatrixDecorator takes care on outputting distance results formatted like a
    distance matrix. It differentiates between normalized and not normalized distance results.

    Format to expect looks like this:
    [                               <- start of matrix
        [                           <- start of a tree
            [p1e1t1, ..., pne1t1],  <- list of distance events per prototype
            ...,
            [p1ent1, ..., pnent1]   <- for each ensemble
        ],
        ...
        [
            [p1e1tn, ..., pne1tn],
            ...,
            [p1entn, ..., pnentn]
        ]
    ]
    """
    def __init__(self, normalized=False):
        if normalized:
            Decorator.__init__(self, name="normalized_matrix")
        else:
            Decorator.__init__(self, name="matrix")
        self._data = None
        self._tmp_prototype_counts = None
        self._normalized = normalized

    def data(self):
        if self._data is not None:
            results = []
            for result in self._data:
                # on level of ensembles
                results.append([])
                for single in result:
                    adapted = [value if value >= 0 else 0 for value in single]
                    results[-1].append(adapted)
            return results
        return None

    def _algorithm_updated(self):
        self._data = []
        self._tmp_prototype_counts = None

    def _tree_started(self):
        size = self._matrix_size()
        if self._data and size < len(self._data) + 1:
            raise MatrixDoesNotMatchBounds(size, size, len(self._data) + 1)
        # add a new row for a new algorithm for each ensemble
        self._data.append([[0 for _ in self.algorithm.prototypes]
                           for _ in range(self.algorithm.signature.count)])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()

    def _event_added(self, event, result):
        # Format of result: [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]
        # TODO: might be changed to _tree_finished
        size = self._matrix_size()
        if size < len(result[0]):
            raise MatrixDoesNotMatchBounds(size, len(result), len(self._data))
        event_counts = self._algorithm.event_counts()
        for i, ensemble_result in enumerate(result):
            for j, prototype_result in enumerate(ensemble_result):
                if self._normalized:
                    self._data[-1][i][j] = result[i][j] / float(
                        event_counts[i][j] + self._tmp_prototype_counts[i][j])
                else:
                    self._data[-1][i][j] = result[i][j]

    def _matrix_size(self):
        if self._data is None:
            self._data = [[]]
        if len(self._data) > 0:
            return len(self._algorithm.prototypes)
        return 0

    def _update(self, decorator):
        self._data.extend(decorator.data())
