import os

from assess.decorators.decorator import Decorator


class PerformanceDecorator(Decorator):
    def __init__(self):
        Decorator.__init__(self)
        self._items = ["user time", "system time", "children's user time", "children's system time", "elapsed real time"]
        self._performances = []

    @Decorator.algorithm.setter
    def algorithm(self, value):
        Decorator.algorithm.__set__(self, value)
        self._performances.append([])

    def add_event(self, event, **kwargs):
        start = os.times()
        result = self._algorithm.add_event(event, **kwargs)
        end = os.times()
        self._performances[-1].append([end[i]-start[i] for i in range(0, len(start))])
        return result

    def performances(self):
        return self._performances

    def accumulated_performances(self):
        results = []
        for performance in self._performances:
            result = [0 for i in range(0, len(performance[0]))]
            for values in performance:
                for i in range(0, len(values)):
                    result[i] += values[i]
            results.append(result)
        return results
