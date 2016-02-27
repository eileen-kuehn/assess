class Decorator(object):
    def __init__(self):
        self._algorithm = None
        self.decorator = None

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        if self.decorator:
            self.decorator.algorithm = value
        self._algorithm = value
        self._algorithm_updated()

    def _algorithm_updated(self):
        pass

    def add_event(self, event, **kwargs):
        self._event_will_be_added()
        if self.decorator:
            result = self.decorator.add_event(event, **kwargs)
        else:
            result = self._algorithm.add_event(event, **kwargs)
        self._event_added(event, result[:])
        return result

    def _event_will_be_added(self):
        pass

    def _event_added(self, event, result):
        pass

    def data(self):
        raise NotImplementedError()

    def accumulated_data(self):
        raise NotImplementedError()
