import os

from assess.decorators.decorator import Decorator


class PerformanceDecorator(Decorator):
    def __init__(self, accumulated=True):
        Decorator.__init__(self)
        self._items = ["user time", "system time", "children's user time", "children's system time", "elapsed real time"]
        self._performances = []
        self._start = None
        self._accumulated = accumulated
        if self._accumulated:
            self._name = "accumulated_performance"
        else:
            self._name = "performance"

    def _algorithm_updated(self):
        self._performances = []
        self._start = None

    def _tree_started(self):
        # TODO: algorithm description should be given by another decorator
        # TODO: there should be another decorator describing the data itself
        self._performances.append({})

    def _event_will_be_added(self):
        self._start = os.times()

    def _event_added(self, event, result):
        if event is None:
            return
        end = os.times()
        result_dict = zip(self._items, [end[i] - self._start[i] for i in range(len(self._start))])
        self._start = None
        for key, value in result_dict:
            self._performances[-1].setdefault(key, []).append(value)

    def data(self):
        if self._accumulated:
            result = []
            for performance in self._performances:
                result.append({})
                for key in performance:
                    try:
                        result[-1][key] = sum(performance[key])
                    except TypeError:
                        result[-1][key] = performance[key]
            return result
        else:
            return self._performances

