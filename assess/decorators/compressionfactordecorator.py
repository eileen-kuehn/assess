"""
This module offers a decorator to track information on actual compression for monitoring tree as
well as prototypes.
"""

from assess.decorators.decorator import Decorator


class CompressionFactorDecorator(Decorator):
    """
    The CompressionFactorDecorator outputs information about the actual compression that is
    produced by using a single kind of signature.

    Returns data regarding ensembles in the following format:
    {
        "prototypes": [[p1e1, ..., pne1], ... [p1en, ..., pnen]],
        "monitoring": [
            [ve1t1, ..., vent1],
            ...
            [ve1tn, ..., ventn]
        ],
        "accumulated": [ve1, ..., ven]
    }

    The prototype gives information on how many nodes for a prototype are compressed regarding a
    given ensemble.
    The monitoring gives information on how many nodes for the monitoring tree are compressed
    regarding a given ensemble. This is appended for each tree that is processed.
    The accumulated gives information on how many nodes for all prototypes are compressed
    regarding a given ensemble.
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
        original = self._algorithm.tree.node_count()  # value
        if original == 0:
            return [0]
        node_counts = self._algorithm.signature_tree.node_count()  # [ve1, ..., ven]
        return [1.0 - (node_count / float(original)) for node_count in node_counts]

    def _compression_factor(self):
        # list of sizes [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        original = self._original_sizes()
        # list of sizes [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        compressed = self._compressed_size()
        return [[1.0 - compressed[i][j] / float(original[i][j]) for j in range(
            len(compressed[0]))] for i in range(len(compressed))]

    def _accumulated_compression_factor(self):
        """
        Accumulated compression is a list of accumulated compression by ensemble. For convenience
        in accessing the datastructure, each item is put inside a list again, e.g.
        [compression_e1, ..., compression_en]

        :return: list of compression factors by ensemble
        """
        original = [sum(element) for element in self._original_sizes()]  # [sum1, ..., sumn]
        if original[0] == 0:
            return []
        converted = self._algorithm.signature_prototypes
        try:
            compressed = converted.node_count()  # [ve1, ..., ven]
        except AttributeError:
            compressed = [sum(element) for element in self._compressed_size()]
        return [1.0 - compressed[i] / float(original[i]) for i in range(len(compressed))]

    def data(self):
        return self._compressions

    def _original_sizes(self):
        """
        Returns number of nodes a prototype consists of.
        :return:
        """
        return self._algorithm.prototype_node_counts(signature=False)

    def _compressed_size(self):
        return self._algorithm.prototype_node_counts(signature=True)

    def _update(self, decorator):
        self._compressions["monitoring"].extend(decorator.data()["monitoring"])
