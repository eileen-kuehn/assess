from assess.decorators.decorator import Decorator
from assess.events.events import ProcessStartEvent
from assess.exceptions.exceptions import MatrixDoesNotMatchBounds


class DistanceMatrixDecorator(Decorator):
    def __init__(self, normalized=False):
        Decorator.__init__(self)
        self._distance_matrix = None
        self._tmp_prototype_counts = None
        self._normalized = normalized
        if self._normalized:
            self._name = "normalized_matrix"
        else:
            self._name = "matrix"

    def data(self):
        results = []
        for result in self._distance_matrix:
            adapted = [value if value >= 0 else 0 for value in result]
            results.append(adapted)
        return results

    def _algorithm_updated(self):
        self._distance_matrix = None
        self._tmp_prototype_counts = None

    def _tree_started(self):
        size = self._matrix_size()
        if 0 < size <= len(self._distance_matrix):
            raise MatrixDoesNotMatchBounds(size, size, len(self._distance_matrix) + 1)
        # add a new row for a new algorithm
        self._distance_matrix.append([0 for _ in range(self._matrix_size())])

    def _event_added(self, event, result):
        size = self._matrix_size()
        if 0 < size != len(result):
            raise MatrixDoesNotMatchBounds(size, len(result), len(self._distance_matrix))
        if self._normalized:
            if self._tmp_prototype_counts is None:
                self._tmp_prototype_counts = self._algorithm.prototype_event_counts()
            event_counts = self._algorithm.event_counts()
            for i in range(len(result)):
                result[i] /= float(event_counts[i]+self._tmp_prototype_counts[i])
        self._distance_matrix[-1] = result

    def _matrix_size(self):
        if self._distance_matrix is None:
            self._distance_matrix = []
        if len(self._distance_matrix) > 0:
            return len(self._distance_matrix[0])
        return 0
