"""
This module implements a base decorator for ASSESS. It ensures the correct
encapsulation of decorators and wraps the actual algorithm being used.
"""
import types

from assess.exceptions.exceptions import DecoratorNotFoundException


class EventWrapper(object):
    def __init__(self):
        self._signature = None
        self.type = None

    @property
    def signature(self):
        return self._signature

    @signature.setter
    def signature(self, value):
        if not isinstance(value, list):
            self._signature = [value]
        else:
            self._signature = value


class Decorator(object):
    """
    Base decorator for ASSESS to measure different statistics based on methods
    of algorithm class.
    """
    def __init__(self, name="decorator"):
        self._algorithm = None
        self.decorator = None
        self._name = name
        self._last_event_counts = None

    @staticmethod
    def from_name(name):
        if "anomaly" in name:
            from assess.decorators.anomalydecorator import AnomalyDecorator
            # FIXME: how to pass parameter?
            return AnomalyDecorator()
        elif "normalized_ensembles" in name:
            from assess.decorators.ensemblematrixdecorator import \
                EnsembleMatrixDecorator
            return EnsembleMatrixDecorator(normalized=True)
        elif "normalized_ensembledistances" in name:
            from assess.decorators.ensembledistancedecorator import \
                EnsembleDistanceDecorator
            return EnsembleDistanceDecorator(normalized=True)
        elif "ensembledistances" in name:
            from assess.decorators.ensembledistancedecorator import \
                EnsembleDistanceDecorator
            return EnsembleDistanceDecorator(normalized=False)
        elif "ensembleanomaly" in name:
            from assess.decorators.ensembleanomalydecorator import \
                EnsembleAnomalyDecorator
            return EnsembleAnomalyDecorator()
        elif "compression" in name:
            from assess.decorators.compressionfactordecorator import \
                CompressionFactorDecorator
            return CompressionFactorDecorator()
        elif "data" in name:
            from assess.decorators.datadecorator import DataDecorator
            return DataDecorator()
        elif "normalized_ensembles" in name:
            from assess.decorators.ensemblematrixdecorator import \
                EnsembleMatrixDecorator
            return EnsembleMatrixDecorator(normalized=True)
        elif "ensembles" in name:
            from assess.decorators.ensemblematrixdecorator import \
                EnsembleMatrixDecorator
            return EnsembleMatrixDecorator(normalized=False)
        elif "normalized_distances" in name:
            from assess.decorators.distancedecorator import \
                DistanceDecorator
            return DistanceDecorator(normalized=True)
        elif "distances" in name:
            from assess.decorators.distancedecorator import \
                DistanceDecorator
            return DistanceDecorator(normalized=False)
        elif "normalized_matrix" in name:
            from assess.decorators.distancematrixdecorator import \
                DistanceMatrixDecorator
            return DistanceMatrixDecorator(normalized=True)
        elif "matrix" in name:
            from assess.decorators.distancematrixdecorator import \
                DistanceMatrixDecorator
            return DistanceMatrixDecorator(normalized=False)
        elif "accumulated_distance_performance" in name:
            from assess.decorators.distanceperformancedecorator import \
                DistancePerformanceDecorator
            return DistancePerformanceDecorator(accumulated=True)
        elif "distance_performance" in name:
            from assess.decorators.distanceperformancedecorator import \
                DistancePerformanceDecorator
            return DistancePerformanceDecorator(accumulated=False)
        elif "accumulated_performance" in name:
            from assess.decorators.performancedecorator import \
                PerformanceDecorator
            return PerformanceDecorator(accumulated=True)
        elif "performance" in name:
            from assess.decorators.performancedecorator import \
                PerformanceDecorator
            return PerformanceDecorator(accumulated=False)
        elif "accumulated_signature_performance" in name:
            from assess.decorators.signatureperformancedecorator import \
                SignaturePerformanceDecorator
            return SignaturePerformanceDecorator(accumulated=True)
        elif "signature_performance" in name:
            from assess.decorators.signatureperformancedecorator import \
                SignaturePerformanceDecorator
            return SignaturePerformanceDecorator(accumulated=False)
        elif "signature" in name:
            from assess.decorators.signaturedecorator import \
                SignatureDecorator
            return SignatureDecorator()
        elif "ensembles" in name:
            from assess.decorators.ensemblematrixdecorator import \
                EnsembleMatrixDecorator
            return EnsembleMatrixDecorator(normalized=False)

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
        self._last_event_counts = None
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
            result = self._algorithm.__class__.add_event(
                self._algorithm, event, **kwargs)
        if result is not None:
            # Functionality has been changed to a list of results, so for each
            # result the internal method :py:meth:_event_added is called
            # TODO: maybe inform internal method about the actual event
            # difference per step?
            tmp_event = EventWrapper()
            for index, single_result in enumerate(result[:]):
                # given the assumption that none of the decorators requires
                # the event but the signature decorator requires single list of
                # signatures, we will prepare the event accordingly
                tmp_event.signature = event.signature[index]
                tmp_event.type = type(event)
                self._event_added(tmp_event, single_result)
        return result

    def update(self, decorator):
        """
        This method is intended to update a specific decorator with another part.
        This is especially useful when using multiprocessing. Then it might happen,
        that a single run is splitted into several parts that should afterwards
        be recombined.

        :param decorator: A decorator to add to current values
        """
        while decorator is not None:
            if self._compatible(decorator):
                self._update(decorator)
            else:
                current_decorator = self.decorator
                while current_decorator is not None:
                    if current_decorator._compatible(decorator):
                        current_decorator._update(decorator)
                        break
                    else:
                        current_decorator = current_decorator.decorator
                if current_decorator is None:
                    raise DecoratorNotFoundException(decorator=decorator)
            decorator = decorator.decorator

    def _compatible(self, decorator):
        return decorator._name == self._name

    def _update(self, decorator):
        pass

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
        Method to receive the data that was collected by the decorator.
        It also includes a description about the decorator itself to be
        self-explanatory in e.g. json output.

        :return: Descriptive string containing the data
        """
        result = {self._name: self.data()}
        if self.decorator:
            result.update(self.decorator.descriptive_data())
        return result
