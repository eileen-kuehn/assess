from assess.decorators.decorator import Decorator


class CompressionFactorDecorator(Decorator):
    def __init__(self):
        Decorator.__init__(self)
        self._compressions = []

    def _algorithm_updated(self):
        self._compressions.append(self.compression_factor())

    def compression_factor(self):
        return 1.0 - self._compressed_size() / float(self._original_size())

    def compression_factors(self):
        return self._compressions

    def _original_size(self):
        count = 0
        for prototype in self._algorithm.prototypes:
            count += prototype.node_count()
        return count

    def _compressed_size(self):
        count = 0
        converted = self._algorithm.prototypes_converted_for_algorithm()
        if isinstance(converted, dict):
            count = len(converted.keys())
        elif isinstance(converted, list):
            count = 0
            for prototype in converted:
                count += prototype.node_count()
        return count
