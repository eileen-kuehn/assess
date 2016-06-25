"""
Module offers an incremental method to split underlying distributions to more correctly represent
the underlying data for distance measurement.
"""
import bisect

from assess.algorithms.statistics.statistics import MeanVariance


class SplittedStatistics(object):
    """
    The class SplittedStatistics takes different values and incrementally clusters given values
    while summarising using a specified statistic type. The clustering concept is based on

    * density based clustering, and
    * gravity based cluster merging (currently not implemented)

    It is taken care, that at least statistics as possible are stored. This can be configured
    via specifying threshold and attraction factor.

    Attention: the attraction factor is currently not in use.
    """
    def __init__(self, statistics_type=MeanVariance, threshold=.5, attraction_factor=None):
        self._statistics_type = statistics_type
        self._statistics = [statistics_type(value=0)]
        self._threshold = threshold
        self._attraction_factor = attraction_factor

    def add(self, value):
        """
        Method to add a specific value. Depending on the value, it is either added to existing
        statistics data set, or a new one is created.

        :param value: New value to add
        """
        # look for closest statistics_type dataset
        if value == 0:
            self._statistics[0].add(value=value)
        else:
            distance, index = self._closest_value_and_index(value=value)
            if distance > self._threshold:
                # check where to insert value
                if (self._statistics[index - 1]._mean if index > 0 else -float("inf")) < value < \
                        (self._statistics[index]._mean):
                    self._statistics.insert(index, self._statistics_type(value=value))
                else:
                    self._statistics.insert(index + 1, self._statistics_type(value=value))
            else:
                self._statistics[index].add(value=value)
                # perform merging
                try:
                    while self._statistics[index].object_distance(self._statistics[index + 1]) <= 1:
                        self._statistics[index].update(statistics=self._statistics[index + 1])
                        del self._statistics[index + 1]
                except IndexError:
                    pass
                try:
                    while not (not (index > 0) or not (
                        self._statistics[index].object_distance(self._statistics[index - 1]) <= 1)):
                        self._statistics[index - 1].update(statistics=self._statistics[index])
                        del self._statistics[index]
                        index -= 1
                except IndexError:
                    pass

    @property
    def count(self):
        """
        Get the number of values that went into the statistics calculation.

        :return: Count of considered values
        """
        result = 0
        for statistic in self._statistics:
            result += statistic.count
        return result

    def distance(self, value=None):
        """
        Check the current distance for a given value.
        If no value is given, None is returned.

        :param value: The value to check the distance for
        :return: Distance
        """
        # return distance to closest match
        distance = None
        if value is not None:
            distance, _ = self._closest_value_and_index(value=value)
        return distance

    def _closest_value_and_index(self, value):
        """
        Method determines the closest value and index for given value from current statistics.

        :param value: reference value to look for
        :return: tuple from distance and index of closest value
        """
        if len(self._statistics) > 1:
            index = bisect.bisect_left(
                [statistic._mean for statistic in self._statistics],
                value,
                lo=1
            )
            left_distance = self._statistics[index - 1].distance(value=value) \
                if index > 1 else float("inf")
            right_distance = self._statistics[index].distance(value=value) \
                if index < len(self._statistics) else float("inf")
            return min(left_distance, right_distance), index \
                if right_distance < left_distance else index - 1
        return 1.0, 0
