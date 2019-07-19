"""
This module provides a decorator that gives general information about the data.
"""

from assess.decorators.decorator import Decorator


class DataDecorator(Decorator):
    """
    The DataDecorator collects information on the node count of currently
    analysed prototypes.

    Returns data regarding ensembles in the following format:
    {
        "prototypes": {
            "original": [[p1e1, ..., pne1], ..., [p1en, ..., pnen]]
            "converted": [[p1e1, ..., pne1], ..., [p1en, ..., pnen]]
        },
        "monitoring": {
            "original": [[ve1t1, ..., vent1], ..., [ve1tn, ..., ventn]]
            "converted": [[ve1t1, ..., vent1], ..., [ve1tn, ..., ventn]]
        }
    }
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
                "monitoring": {}
            }
        else:
            self._data["monitoring"]["original"].append(None)
            self._data["monitoring"]["converted"].append(None)

    def _tree_finished(self, result):
        self._data["monitoring"].setdefault("original", [None])[-1] = \
            [self._algorithm.tree.node_count()]
        self._data["monitoring"].setdefault("converted", [None])[-1] = \
            self._algorithm.distance.node_count(signature=True)

    def data(self):
        return self._data

    def _update(self, decorator):
        self._data["monitoring"].setdefault("original", []).extend(
            decorator.data()["monitoring"].get("original", []))
        self._data["monitoring"].setdefault("converted", []).extend(
            decorator.data()["monitoring"].get("converted", []))

    def __iadd__(self, other):
        try:
            if other.col_idx[0] not in self.col_idx:
                for key in ["original", "converted"]:
                    for index, ensemble_values in enumerate(
                            other._data["prototypes"][key]):
                        self._data["prototypes"][key][index].extend(ensemble_values)
                self.col_idx.extend(other.col_idx)
            if other.row_idx[0] not in self.row_idx:
                for key in ["original", "converted"]:
                    self._data["monitoring"][key].extend(other._data["monitoring"][key])
                self.row_idx.extend(other.row_idx)
            return self
        except AttributeError:
            pass
        return NotImplemented
