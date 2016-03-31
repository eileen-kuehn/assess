from assess.decorators.decorator import Decorator


class DistanceDecorator(Decorator):
    def __init__(self, normalized=False):
        Decorator.__init__(self)
        self._distances = []
        self._normalized = normalized
        if self._normalized:
            self._name = "normalized_distances"
        else:
            self._name = "distances"
        self._tmp_prototype_counts = None

    def data(self):
        return self._distances

    def _algorithm_updated(self):
        self._distances = []
        self._tmp_prototype_counts = None

    def _tree_started(self):
        self._distances.append([[] for value in range(len(self._algorithm.prototypes))])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_counts(original=False)

    def _event_added(self, event, result):
        node_counts = self._algorithm.node_counts(original=False)
        for i in range(len(result)):
            if self._normalized:
                self._distances[-1][i].append(result[i] / float(node_counts[i]+self._tmp_prototype_counts[i]))
            else:
                self._distances[-1][i].append(result[i])
