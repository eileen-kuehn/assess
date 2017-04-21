from assess.decorators.decorator import Decorator

from assess.algorithms.distances.ensembledistance import mean_ensemble_distance, mean_ensemble_event_counts, normalise_distance
from assess.events.events import ProcessStartEvent, ProcessExitEvent


class EnsembleAnomalyDecorator(Decorator):
    """
    The ensemble anomaly detector works on ensembles and thus first summarises the distances and
    based on this, determines for each event if it is handled as an anomaly or not.
    If it might be an anomaly, True is appended, False otherwise.

    The results are given in the following format:
    [
        [                                       <- start of a tree
            [                                   <- start of an ensemble (for generic reading)
                [v1p1t1, ..., vnpnt1]           <- list of anomaly events per prototype
            ]
            ...
            [
                [v1p1ent1, ..., vnpnent1]
            ]
        ]
    ]
    """
    def __init__(self, percentage=0.1):
        Decorator.__init__(self, name="ensembleanomaly")
        self._data = []
        self._tmp_prototype_counts = None
        self._band_widths = None
        self._tmp_event_weights = None
        self._percentage = percentage
        self._last_result = None
        self._mismatches = None
        self._enhanced_mismatches = None
        self._start_mismatch_counter = None  # early-counting of exit events

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._tmp_prototype_counts = None
        self._tmp_event_weights = None

    def _tree_started(self):
        self._data.append([[[] for _ in self._algorithm.prototypes]])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()
            self._tmp_prototype_counts = [[mean_ensemble_distance(value) for value in zip(*self._tmp_prototype_counts)]]
            self._threshold = [[self._percentage * value / float(1 - self._percentage) for value in self._tmp_prototype_counts[0]]]
        if self._tmp_event_weights is None:
            self._tmp_event_weights = self._algorithm.distance.weights()
        self._last_result = self._tmp_prototype_counts
        self._mismatches = [[0 for _ in self._algorithm.prototypes]]
        self._enhanced_mismatches = [[0 for _ in self._algorithm.prototypes]]
        self._start_mismatch_counter = [[0 for _ in self._algorithm.prototypes]]

    def _tree_finished(self, result):
        # Format for result: [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]
        event_counts = [mean_ensemble_distance(value) for value in zip(*self._algorithm.event_counts())]
        if result is not None:
            # -> reformat result to: [[v1p1, ..., vnpn]]
            formatted_result = [[mean_ensemble_distance(value) for value in zip(*result)]]
        else:
            formatted_result = [[mean_ensemble_distance(value) for value in
                                 self.algorithm.distance.iter_on_prototypes(self._algorithm.prototypes)]]
        for i, ensemble_result in enumerate(formatted_result):
            for j, prototype_result in enumerate(ensemble_result):
                normalised_distance = normalise_distance(distance=prototype_result,
                                                         size_prototype=self._tmp_prototype_counts[i][j],
                                                         size_tree=event_counts[j])
                self._data[-1][i][j].append(0 if normalised_distance <= self._percentage else 2)

    def _event_added(self, event, result):
        # Format for result: [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]
        # -> reformat result to [[v1p1, ..., vnpn]]
        formatted_result = [[mean_ensemble_distance(value) for value in zip(*result)]]

        for ensemble_idx, ensemble in enumerate(formatted_result):
            for prototype_index, prototype in enumerate(ensemble):
                if prototype > self._last_result[ensemble_idx][prototype_index]:
                    mismatch = prototype - self._last_result[ensemble_idx][prototype_index]
                    self._mismatches[ensemble_idx][prototype_index] += mismatch
                    if event.type == ProcessStartEvent and self._tmp_event_weights[ProcessStartEvent] == mismatch:
                        self._enhanced_mismatches[ensemble_idx][prototype_index] += mismatch + self._tmp_event_weights[ProcessExitEvent]
                        self._start_mismatch_counter[ensemble_idx][prototype_index] += 1
                    elif (event.type == ProcessExitEvent and
                                  self._tmp_event_weights[ProcessExitEvent] == mismatch and
                                  self._start_mismatch_counter[ensemble_idx][prototype_index] > 0):
                        # ignore mismatch and decrease counter
                        self._start_mismatch_counter[ensemble_idx][prototype_index] -= 1
                    else:
                        self._enhanced_mismatches[ensemble_idx][prototype_index] += mismatch
        for idx, prototype in enumerate(self._mismatches[0]):
            if prototype > self._threshold[0][idx]:
                self._data[-1][0][idx].append(2)
            elif self._enhanced_mismatches[0][idx] > self._threshold[0][idx]:
                self._data[-1][0][idx].append(1)
            else:
                self._data[-1][0][idx].append(0)
        self._last_result = formatted_result

    def _update(self, decorator):
        self._data.extend(decorator.data())

    def __iadd__(self, other):
        """
        [                                       [
            [                                       [ <- start of a tree
                [                                       [ <- start of an ensemble
                    [v1p1e1t1, ..., vnp1e1t1],              [v1p3e1t1], ..., [vnp3e1t1],
                    [v1p2e1t1, ..., vnp2e1t1]               [v1p4e1t1], ..., [vnp4e1t1]
                ]                                       ]
                ...                                     ...
                [                                       [
                    [v1p1ent1, ..., vnpnent1],              [v1p3ent1], ..., [vnp3ent1],
                    [v1p2ent1, ..., vnp2ent1]               [v1p4ent1], ..., [vnp4ent1]
                ]                                       ]
            ]                                       ]
        ]                                       ]
        :param other:
        :return:
        """
        for tree_idx, tree_values in enumerate(other._data):
            for ensemble_idx, ensemble_values in enumerate(tree_values):
                self[tree_idx][ensemble_idx].extend(ensemble_values)
        return self
