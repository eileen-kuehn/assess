from assess.decorators.decorator import Decorator


class DataDecorator(Decorator):
    def __init__(self):
        Decorator.__init__(self)
        self._data = None

    def _algorithm_updated(self):
        if not self._data:
            # measure size of prototypes to compare with
            self._data = [prototype.node_count() for prototype in self._algorithm._prototypes]

    def data(self):
        return self._data
