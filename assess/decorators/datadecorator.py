"""
This module provides a decorator that gives general information about the data.
"""

from assess.decorators.decorator import Decorator


class DataDecorator(Decorator):
    """
    The DataDecorator collects information on the node count of currently analysed prototypes.
    """
    def __init__(self):
        Decorator.__init__(self, name="data")
        self._data = None

    def _algorithm_updated(self):
        self._data = None

    def _tree_started(self):
        if not self._data:
            # measure size of prototypes to compare with
            self._data = {
                "prototypes": {
                    "original": self._algorithm.prototype_node_counts(signature=False),
                    "converted": self._algorithm.prototype_node_counts(signature=True)
                },
                "monitoring": [{}]
            }
        else:
            self._data["monitoring"].append(dict())

    def _tree_finished(self, result):
        self._data["monitoring"][-1] = {
            "original": self._algorithm.tree.node_count(),
            "converted": self._algorithm.signature_tree.node_count()
        }

    def data(self):
        return self._data

    def _update(self, decorator):
        self._data["monitoring"].extend(decorator.data()["monitoring"])
