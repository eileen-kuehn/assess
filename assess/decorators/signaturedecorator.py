from assess.decorators.decorator import Decorator


class SignatureDecorator(Decorator):
    """
    The SignatureDecorator outputs for each event the current signature it calculated and returns
    in form of a vector.
    """
    def __init__(self):
        Decorator.__init__(self, name="signature")
        self._data = []
        self._last_event_counts = None

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._last_event_counts = None

    def _tree_started(self):
        self._data.append([])

    def _tree_finished(self, result):
        self._last_event_counts = None

    def _event_added(self, event, result):
        # info about current progress
        event_counts = self._algorithm.event_counts()
        # TODO: this check might be done in base Decorator
        if self._last_event_counts is None or event_counts[0] > self._last_event_counts[0]:
            try:
                self._data[-1].append(event.signature)
            except AttributeError:
                self._data[-1].append("unknown")
            self._last_event_counts = event_counts

    def _update(self, decorator):
        self._data.extend(decorator.data())
