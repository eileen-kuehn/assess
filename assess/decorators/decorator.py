import types


class Decorator(object):
    def __init__(self, name="decorator"):
        self._algorithm = None
        self.decorator = None
        self._name = name

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        if self.decorator:
            self.decorator.algorithm = value
        self._algorithm = value
        self._algorithm_updated()

    def wrap_algorithm(self, algorithm):
        """
        Wrap an algorithm, and replace its methods with our own

        Recurses through all linked ``decorator`` elements.
        """
        if self.decorator is not None:
            self.decorator.wrap_algorithm(algorithm)
        self._algorithm = algorithm
        self._algorithm_updated()
        # replace all methods with our own ones
        for name in dir(algorithm):
            if name.startswith("__"):
                continue
            try:
                my_value = getattr(self, name)
            except AttributeError:
                continue
            else:
                if isinstance(my_value, (types.MethodType, types.FunctionType)):
                    setattr(algorithm, name, my_value)

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
            self._algorithm.__class__.start_tree(self._algorithm, **kwargs)
        self._tree_started()

    def finish_tree(self):
        if self.decorator:
            result = self.decorator.finish_tree()
        else:
            result = self._algorithm.__class__.finish_tree(self._algorithm)
        self._tree_finished(result[:] if result is not None else None)
        return result

    def add_event(self, event, **kwargs):
        self._event_will_be_added()
        if self.decorator:
            result = self.decorator.add_event(event, **kwargs)
        else:
            result = self._algorithm.__class__.add_event(self._algorithm, event, **kwargs)
        if result is not None:
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
