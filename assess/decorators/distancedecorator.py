from assess.decorators.decorator import Decorator


class DistanceDecorator(Decorator):
    def __init__(self):
        self._distances = []
        self._name = "distances"

    def data(self):
        return self._distances

    def _algorithm_updated(self):
        self._distances = []

    def _tree_started(self):
        self._distances.append([[] for value in range(len(self._algorithm.prototypes))])

    def _event_added(self, event, result):
        for i in range(len(result)):
            self._distances[-1][i].append(result[i])
