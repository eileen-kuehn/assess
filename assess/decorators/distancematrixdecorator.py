from assess.decorators.decorator import Decorator
from assess.events.events import ProcessStartEvent
from assess.exceptions.exceptions import MatrixDoesNotMatchBounds


class DistanceMatrixDecorator(Decorator):
    def __init__(self, normalized=False):
        Decorator.__init__(self)
        self._distance_matrix = None
        self._event_counter = 0
        self._normalized = normalized

        self._tmp_prototype_counts = None

    def data(self):
        results = []
        for result in self._distance_matrix:
            adapted = [value if value >= 0 else 0 for value in result]
            results.append(adapted)
        return results

    def _algorithm_updated(self):
        size = self._matrix_size()
        if 0 < size <= len(self._distance_matrix):
            raise MatrixDoesNotMatchBounds(size, size, len(self._matrix_size()) + 1)
        # add a new row for a new algorithm
        self._distance_matrix.append([0 for x in range(self._matrix_size())])

    def _event_added(self, event, result):
        size = self._matrix_size()
        if 0 < size != len(result):
            raise MatrixDoesNotMatchBounds(size, len(result), len(self._distance_matrix))
        if type(event) is ProcessStartEvent:
            self._event_counter += 1
        if self._normalized:
            if self._tmp_prototype_counts is None:
                self._tmp_prototype_counts = self._algorithm.prototype_counts(original=False)
            node_counts = self._algorithm.node_counts(original=False)
            for i in range(len(result)):
                result[i] /= float(node_counts[i]+self._tmp_prototype_counts[i])
        self._distance_matrix[-1] = result

    def _matrix_size(self):
        if self._distance_matrix is None:
            self._distance_matrix = []
        if len(self._distance_matrix) > 0:
            return len(self._distance_matrix[0])
        return 0
