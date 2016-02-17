from assess.decorators.decorator import Decorator
from assess.events.events import ProcessStartEvent
from assess.exceptions.exceptions import MatrixDoesNotMatchBounds


class DistanceMatrixDecorator(Decorator):
    def __init__(self, normalized=False):
        Decorator.__init__(self)
        self._distance_matrix = []
        self._event_counter = 0
        self._normalized = normalized

    @property
    def distance_matrix(self):
        return self._distance_matrix

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
        self._distance_matrix[-1] = result if not self._normalized else \
            [value/float(self._event_counter) for value in result]

    def _matrix_size(self):
        if len(self._distance_matrix) > 0:
            return len(self._distance_matrix[0])
        return 0
