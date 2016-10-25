# FIXME: still needs conversion to new data structure
from assess.decorators.decorator import Decorator


class AnomalyDecorator(Decorator):
    def __init__(self, percentage=0.1):
        Decorator.__init__(self, name="anomaly")
        self._data = []
        self._last_event_counts = None
        self._tmp_prototype_counts = None
        self._percentage = percentage

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._last_event_counts = None
        self._tmp_prototype_counts = None

    def _tree_started(self):
        self._data.append([[] for _ in self._algorithm.prototypes])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()

    def _tree_finished(self, result):
        ranges = [(0, max_value * self._percentage) for max_value in self._tmp_prototype_counts]
        if result is not None:
            [self._data[-1][index].append(not ranges[index][0] <= result[index] <= ranges[index][1])
                for index in xrange(len(result))]
        else:
            try:
                for index, distance in enumerate(self.algorithm.distance):
                    self._data[-1][index].append(not ranges[index][0] <= distance <= ranges[index][1])
            except AttributeError:
                pass
        self._last_event_counts = None

    def _event_added(self, event, result):
        # info about current progress
        event_counts = self._algorithm.event_counts()
        # the event differs from the last one, so take the values
        ranges = self._current_range(progress=event_counts[0])
        [self._data[-1][index].append(not ranges[index][0] <= result[index] <= ranges[index][1])
            for index in xrange(len(result))]

    def _update(self, decorator):
        self._data.extend(decorator.data())

    def _current_range(self, progress):
        # expected_distance = -progress + max(prototype)
        # lower bound
        lower = [-progress + count for count in self._tmp_prototype_counts]
        # upper bound
        # upper = [(-1 + self._percentage) * progress + count for count in self._tmp_prototype_counts]
        upper = [-progress + count * (1 + self._percentage) for count in self._tmp_prototype_counts]
        return zip(lower, upper)
