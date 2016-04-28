import os
from assess.decorators.decorator import Decorator


class SignaturePerformanceDecorator(Decorator):
    def __init__(self, accumulated=True):
        Decorator.__init__(self)
        self._items = ["user time", "system time", "children's user time", "children's system time", "elapsed real time"]
        self._performances = []
        self._start = None
        self._accumulated = accumulated
        if self._accumulated:
            self._name = "accumulated_signature_performance"
        else:
            self._name = "signature_performance"

    def _algorithm_updated(self):
        self._performances = []
        self._start = None

    def _tree_started(self):
        self._performances.append({})

    def create_signature(self, node, parent):
        start = os.times()
        result = self._algorithm.__class__.create_signature(self._algorithm, node, parent)
        end = os.times()
        result_dict = zip(self._items, [end[i] - start[i] for i in range(len(start))])
        for key, value in result_dict:
            self._performances[-1].setdefault(key, []).append(value)
        return result

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
