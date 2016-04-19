class Decorator(object):
    def __init__(self):
        self._algorithm = None
        self.decorator = None
        self._name = "decorator"

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

    def _tree_started(self):
        pass

    def _tree_finished(self, result):
        pass

    def start_tree(self, **kwargs):
        if self.decorator:
            self.decorator.start_tree(**kwargs)
        else:
            self._algorithm.start_tree(**kwargs)
        self._tree_started()

    def finish_tree(self):
        if self.decorator:
            result = self.decorator.finish_tree()
        else:
            result = self._algorithm.finish_tree()
        self._tree_finished(result[:] if result is not None else None)
        return result

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

    def descriptive_data(self):
        result = {self._name: self.data()}
        if self.decorator:
            result.update(self.decorator.descriptive_data())
        return result
