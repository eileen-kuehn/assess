"""
This module offers an implementation to output the different distances for dynamic
trees based on the single events that are processed. The actual output is in form
of a vector.
"""

from assess.decorators.decorator import Decorator


class DistanceDecorator(Decorator):
    """
    The DistanceDecorator takes care to initialize a vector of distances.
    For each event the current distance is given. The class also differentiates
    between normalized and not normalized results.

    The results are given in the following format:
    [
        [                                       <- start of a tree
            [                                   <- start of an ensemble
                [v1p1e1t1, ..., vnp1e1t1],
                ...,
                [v1pne1t1, ..., vnp1e1t1]       <- list of distance events per prototype
            ],
            ...
            [
                [v1p1ent1, ..., vnp1ent1],
                ...,
                [v1pnent1, ..., vnpnent1]
            ]
        ],
        ...
        [
            ...
        ]
    ]
    """
    __slots__ = ("_data", "_normalized", "_tmp_prototype_counts")

    def __init__(self, normalized=False):
        if normalized:
            Decorator.__init__(self, name="normalized_distances")
        else:
            Decorator.__init__(self, name="distances")
        self._data = []
        self._normalized = normalized
        self._tmp_prototype_counts = None

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._tmp_prototype_counts = None

    def _tree_started(self):
        self._data.append([[[] for _ in self._algorithm.prototypes]
                           for _ in range(self.algorithm.signature.count)])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()

    def _event_added(self, event, result):
        # result looks like [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]
        # [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        event_counts = self._algorithm.event_counts()

        for i, ensemble_result in enumerate(result):
            for j, prototype_result in enumerate(ensemble_result):
                if self._normalized:
                    # changed formula to be consistent with distance definition
                    # from thesis
                    self._data[-1][i][j].append(2 * prototype_result / float(
                        event_counts[i][j] + self._tmp_prototype_counts[i][j]
                        + prototype_result))
                else:
                    self._data[-1][i][j].append(result[i][j])

    def _update(self, decorator):
        self._data.extend(decorator.data())

    def __iadd__(self, other):
        for tree_idx, tree_values in enumerate(other._data):
            for ensemble_idx, ensemble_values in enumerate(tree_values):
                self[tree_idx][ensemble_idx].extend(ensemble_values)
        return self
