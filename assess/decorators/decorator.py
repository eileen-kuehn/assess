"""
This module implements a base decorator for ASSESS. It ensures the correct encapsulation of
decorators and wraps the actual algorithm being used.
"""
import types


class Decorator(object):
    """
    Base decorator for ASSESS to measure different statistics based on methods of algorithm class.
    """
    def __init__(self, name="decorator"):
        self._algorithm = None
        self.decorator = None
        self._name = name

    @property
    def algorithm(self):
        """
        Getter property to receive the currently wrapped algorithm.

        :return: Algorithm being wrapped
        """
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        """
        Setter property to set the algorithm to be wrapped.

        :param value: Algorithm to be wrapped
        """
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
        """
        Method start_tree that wraps actual method of algorithm.

        :param kwargs: Additional parameters
        """
        if self.decorator:
            self.decorator.start_tree(**kwargs)
        else:
            self._algorithm.__class__.start_tree(self._algorithm, **kwargs)
        self._tree_started()

    def finish_tree(self):
        """
        Method finish_tree that wraps actual method of algorithm.

        :return: Updated distance
        """
        if self.decorator:
            result = self.decorator.finish_tree()
        else:
            result = self._algorithm.__class__.finish_tree(self._algorithm)
        self._tree_finished(result[:] if result is not None else None)
        return result

    def add_event(self, event, **kwargs):
        """
        Method add_event that wraps actual method of algorithm.

        :param event: Event to be processed
        :param kwargs: Additional parameters
        :return: Updated distance
        """
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
        """
        Method to receive the data that was collected by the decorator.

        :return: Data that was collected
        """
        raise NotImplementedError()

    def descriptive_data(self):
        """
        Method to receive the data that was collected by the decorator. It also includes a
        description about the decorator itself to be self-explanatory in e.g. json output.

        :return: Descriptive string containing the data
        """
        result = {self._name: self.data()}
        if self.decorator:
            result.update(self.decorator.descriptive_data())
        return result
