from assess.decorators.decorator import Decorator


class CompressionFactorDecorator(Decorator):
    def __init__(self):
        Decorator.__init__(self)
        self._compressions = None

    def _algorithm_updated(self):
        if self._compressions is None:
            self._compressions = {
                "prototypes": self._compression_factor(),
                "monitoring": [None],
                "accumulated": self._accumulated_compression_factor()
            }
        else:
            self._compressions["monitoring"].append(None)

    def _event_added(self, event, result):
        self._compressions["monitoring"][-1] = self._monitoring_compression_factor()

    def _monitoring_compression_factor(self):
        return 1.0 - (self._algorithm.node_counts(original=False)[0] /
                      float(self._algorithm.node_counts(original=True)[0]))

    def _compression_factor(self):
        original = self._original_sizes()
        compressed = self._compressed_size()
        return [1.0 - compressed[i] / float(original[i]) for i in range(len(original))]

    def _accumulated_compression_factor(self):
        original = sum(self._original_sizes())
        converted = self._algorithm.prototypes_converted_for_algorithm()
        if isinstance(converted, dict):
            compressed = len(converted.keys())
        elif isinstance(converted, list):
            compressed = 0
            for prototype in converted:
                compressed += prototype.node_count()
        return 1.0 - compressed / float(original)

    def data(self):
        return self._compressions

    def accumulated_data(self):
        # TODO: implement me!
        return 0

    def _original_sizes(self):
        return [prototype.node_count() for prototype in self._algorithm.prototypes]

    def _compressed_size(self):
        return [self._algorithm.node_count_for_prototype(prototype) for prototype in self._algorithm.prototypes]
