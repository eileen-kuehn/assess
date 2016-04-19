from assess.decorators.decorator import Decorator


class DataDecorator(Decorator):
    """
    The DataDecorator collects information on the node count of currently analysed prototypes.
    """
    def __init__(self):
        Decorator.__init__(self)
        self._data = None
        self._name = "data"

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

    def _event_added(self, event, result):
        # TODO: maybe this should only be done once?!
        self._data["monitoring"][-1] = {
            "original": self._algorithm.tree.node_count(),
            "converted": self._algorithm.signature_tree.node_count()
        }

    def data(self):
        return self._data
