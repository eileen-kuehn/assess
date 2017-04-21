"""
This module offers an implementation to output the different distances for dynamic trees based
on the single events that are processed. The actual output is in form of a vector.
"""
from assess.algorithms.distances.ensembledistance import mean_ensemble_distance, normalise_distance
from assess.decorators.decorator import Decorator


class EnsembleDistanceDecorator(Decorator):
    """
    The DistanceDecorator takes care to initialize a vector of distances. For each event the current
    distance is given. The class also differentiates between normalized and not normalized results.

    The results are given in the following format:
    [
        [                                       <- start of a tree
            [                                   <- start of an ensemble
                [v1p1t1, ..., vnp1t1],
                ...,
                [v1pnt1, ..., vnp1t1]           <- list of distance events per prototype
            ]
        ],
        ...
        [
            ...
        ]
    ]
    """
    def __init__(self, normalized=False):
        if normalized:
            Decorator.__init__(self, name="normalized_ensembledistances")
        else:
            Decorator.__init__(self, name="ensembledistances")
        self._data = []
        self._normalized = normalized
        self._tmp_prototype_counts = None

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._tmp_prototype_counts = None

    def _tree_started(self):
        self._data.append([[[] for _ in self._algorithm.prototypes]])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()
            self._tmp_prototype_counts = [[mean_ensemble_distance(value) for value in zip(*self._tmp_prototype_counts)]]

    def _event_added(self, event, result):
        # result looks like [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]
        # formatted_result looks like [[v1p1, ..., vnpn]]
        formatted_result = [[mean_ensemble_distance(value) for value in zip(*result)]]
        # event counts look like [[p1, ..., pn]]
        event_counts = [[mean_ensemble_distance(value) for value in zip(*self._algorithm.event_counts())]]

        for i, ensemble_result in enumerate(formatted_result):
            for j, prototype_result in enumerate(ensemble_result):
                if self._normalized:
                    # changed formula to be consistent with distance definition from thesis
                    self._data[-1][i][j].append(normalise_distance(
                        distance=result[i][j],
                        size_tree=event_counts[i][j],
                        size_prototype=self._tmp_prototype_counts[i][j]))
                else:
                    self._data[-1][i][j].append(result[i][j])

    def _update(self, decorator):
        self._data.extend(decorator.data())

    def __iadd__(self, other):
        for tree_idx, tree_values in enumerate(other._data):
            for ensemble_idx, ensemble_values in enumerate(tree_values):
                self[tree_idx][ensemble_idx].extend(ensemble_values)
        return self
