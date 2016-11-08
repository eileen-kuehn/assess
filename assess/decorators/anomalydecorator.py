from assess.decorators.decorator import Decorator


class AnomalyDecorator(Decorator):
    """
    The anomaly detector works based on each event for given prototypes and ensembles. For each
    event it is determined if it is handled as an anomaly or not. If it might be an anomaly, True
    is appended, False otherwise.

    The results are given in the following format:
    [
        [                                       <- start of a tree
            [                                   <- start of an ensemble
                [v1p1e1t1, ..., vnpne1t1],
                ...,
                [v1pne1t1, ..., vnpne1t1]       <- list of anomaly events per prototype
            ]
            ...
            [
                [v1p1ent1, ..., vnpnent1],
                ...,
                [v1p1ent1, ..., vnpnent1]
            ]
        ]
    ]
    """
    def __init__(self, percentage=0.1):
        Decorator.__init__(self, name="anomaly")
        self._data = []
        self._last_event_counts = None
        self._tmp_prototype_counts = None
        self._percentage = percentage

    def data(self):
        return self._data

    def _algorithm_updated(self):
        self._data = []
        self._last_event_counts = None
        self._tmp_prototype_counts = None

    def _tree_started(self):
        self._data.append([[[] for _ in self._algorithm.prototypes]
                           for _ in range(self._algorithm.signature.count)])
        if self._tmp_prototype_counts is None:
            self._tmp_prototype_counts = self._algorithm.prototype_event_counts()

    def _tree_finished(self, result):
        ranges = self._finished_range()
        if result is not None:
            for i, ensemble_result in enumerate(result):
                for j, prototype_result in enumerate(ensemble_result):
                    self._data[-1][i][j].append(not ranges[i][0] <= result[i][j] <= ranges[i][1])
        else:
            for i, prototype in enumerate(self.algorithm.distance):
                for j, ensemble in enumerate(prototype):
                    self._data[-1][j][i].append(not ranges[j][i][0] <= ensemble <= ranges[j][i][1])
        self._last_event_counts = None

    def _event_added(self, event, result):
        # Format for result: [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]
        event_counts = self._algorithm.event_counts()
        # Format for event counts: [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]
        # Format for prototype event counts: [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]

        # the event differs from the last one, so take the values
        ranges = self._current_range(progress=[elem[0] for elem in event_counts])
        # Format for ranges: [(e1), ..., (en)]

        for i, ensemble_result in enumerate(result):
            for j, prototype_result in enumerate(ensemble_result):
                self._data[-1][i][j].append(not ranges[i][j][0] <= result[i][j] <= ranges[i][j][1])

    def _update(self, decorator):
        self._data.extend(decorator.data())

    def _finished_range(self):
        result = []
        for i, ensemble_result in enumerate(self._tmp_prototype_counts):
            result.append(zip([0 for _ in ensemble_result],
                              [max_value * self._percentage for max_value in ensemble_result]))
        return result

    def _current_range(self, progress):
        # Format for progress: [ve1, ..., ven]
        # expected_distance = -progress + max(prototype)

        # lower bound
        # [[p1e1, p2e1], ..., [p1en, p2en]]
        lower = []
        upper = []
        for ensemble_index, current_progress in enumerate(progress):
            lower.append([-current_progress + count for count in self._tmp_prototype_counts[ensemble_index]])
            upper.append([-current_progress + count * (1 + self._percentage) for count in self._tmp_prototype_counts[ensemble_index]])
        result = [zip(lower[index], upper[index]) for index in range(len(lower))]
        return result
