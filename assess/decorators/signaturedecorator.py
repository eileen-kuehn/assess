from assess.decorators.decorator import Decorator


class SignatureDecorator(Decorator):
    """
    The SignatureDecorator outputs for each event the current signature it calculated and returns
    in form of a vector.
    """
    def __init__(self):
        Decorator.__init__(self, name="signature")
        self._data = []

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._last_event_counts = None

    def _tree_started(self):
        self._data.append([[] for _ in range(self._algorithm.signature.count)])

    def _tree_finished(self, result):
        self._last_event_counts = None

    def _event_added(self, event, result):
        for index, signature in enumerate(event.signature):
            try:
                self._data[-1][index].append(signature)
            except AttributeError:
                self._data[-1][index].append("unknown")

    def _update(self, decorator):
        self._data.extend(decorator.data())
