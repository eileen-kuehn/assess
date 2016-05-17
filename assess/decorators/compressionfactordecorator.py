"""
This module offers a decorator to track information on actual compression for monitoring tree as
well as prototypes.
"""

from assess.decorators.decorator import Decorator


class CompressionFactorDecorator(Decorator):
    """
    The CompressionFactorDecorator outputs information about the actual compression that is
    produced by using a single kind of signature.
    """
    def __init__(self):
        Decorator.__init__(self, name="compression")
        self._compressions = None

    def _algorithm_updated(self):
        self._compressions = None

    def _tree_started(self):
        if self._compressions is None:
            self._compressions = {
                "prototypes": self._compression_factor(),
                "monitoring": [None],
                "accumulated": self._accumulated_compression_factor()
            }
        else:
            self._compressions["monitoring"].append(None)

    def _tree_finished(self, result):
        self._compressions["monitoring"][-1] = self._monitoring_compression_factor()

    def _monitoring_compression_factor(self):
        return 1.0 - (self._algorithm.signature_tree.node_count() /
                      float(self._algorithm.tree.node_count()))

    def _compression_factor(self):
        original = self._original_sizes()
        compressed = self._compressed_size()
        return [1.0 - compressed[i] / float(original[i]) for i in range(len(original))]

    def _accumulated_compression_factor(self):
        original = sum(self._original_sizes())
        converted = self._algorithm.signature_prototypes
        try:
            compressed = converted.node_count()
        except Exception:  # pylint: disable=broad-except
            compressed = sum(self._compressed_size())
        return 1.0 - compressed / float(original)

    def data(self):
        return self._compressions

    def _original_sizes(self):
        return self._algorithm.prototype_node_counts(signature=False)

    def _compressed_size(self):
        return self._algorithm.prototype_node_counts(signature=True)
