"""
Module implements possible methods to represent statistics that might be used for e.g. cluster
representatitives. Currently only MeanVariance is supported.
"""
import math


class Statistics(object):
    """
    The Statistics Class provides the interface for different statistics implementations.

    .. describe:: __add__(other)

       Method returns a new statistics object that contains all data that is contained by the
       statistic itself and the *other* given statistics object.

       If the types under consideration are not equal, a :py:exc:`TypeError` is raised.

    .. describe:: __iadd__(other)

       Method implements the addition of another statistics object. The current statistic is
       updated with the given *other* statistic.

       If the types under consideration are not equal, a :py:exc:`TypeError` is raised.

    .. describe:: __iter__()

       Method iterates over the different values or calculated values that have been stored by
       the given statistic. The given objects do not necessarily have to be the values that were
       originally inserted into the statistics object.

    .. describe:: add(value)

       Method adds another object to the statistics.

    .. describe:: distance(value)

       Returns for a given *value* the distance to the stored objects. A distance of 0 means,
       equality for the given distance. For maximum distance 1 is returned.

    .. describe:: count

       Returns the number of values that have been added to the statistic.

    """
    def __add__(self, other):
        return NotImplemented

    def __iadd__(self, other):
        return NotImplemented

    def __iter__(self):
        return NotImplemented

    def add(self, value):
        """
        Add a given value to the current statistics.

        :param value: Value to be added
        """
        return NotImplemented

    @property
    def count(self):
        """
        Returns the count of objects that went into statistics.

        :return: Current statistics count
        """
        return NotImplemented

    def distance(self, value):
        """
        Returns the distance from the given value to the current statistics. The distance value
        is intended to be in the range [0, 1]. A distance of 0 means the objects are equal. A
        distance of 1 means the biggest possible distance.

        :param value: Value to return distance to.
        :return: Distance in the range [0, 1]
        """
        return NotImplemented


class Statistic(object):
    @property
    def count(self):
        return NotImplemented

    @property
    def value(self):
        return NotImplemented


class MeanVariance(Statistic):
    """
    Supported kind of statistic that can be utilised in SignatureCache to store signatures.
    The MeanVariance class offers a running mean and variance for inserted signatures and their
    assigned values.
    """
    # TODO: I still need to exclude 0 from current statistics stuff
    def __init__(self, value=None):
        self._count = 0
        self._mean = 0.0
        # remember for faster calculation
        self._second_part = None
        self._temporal = 0.0
        if value is not None:
            self.add(value=value)

    def __iadd__(self, statistics):
        """
        Method that updates the current MeanVariance object with the given MeanVariance object.
        Practically, a merging of both objects is performed.

        :param statistics: object which values are merged
        """
        count = self._count + statistics.count
        delta = statistics.mean - self.mean
        self._mean += delta * (statistics.count / count)
        self._temporal += statistics._temporal + (
            delta * delta * self._count * statistics.count / count)
        self._count = count
        return self

    def add(self, value=.0):
        self._count += 1
        delta = value - self._mean
        self._mean += delta / self._count
        self._temporal += delta * (value - self._mean)

    @property
    def mean(self):
        """
        Method returns running mean.

        :return: running mean
        """
        return self._mean

    @property
    def value(self):
        return self._mean

    @property
    def variance(self):
        """
        Variance is None, when not enough values have been collected.

        :return: running variance
        """
        if self._count < 2:
            return None
        return self._temporal / (self._count - 1)

    # def add(self, value=0.0):
    #     """
    #     Method to add a specific value for a given signature to its cache value.
    #     :param value: New value to add
    #     """
    #     self._overall_count += 1
    #     if value != 0:
    #         self._count += 1
    #         new_mean = self._mean + (value - self._mean) / float(self._count)
    #         self._variance += (value - self._mean) * (value - new_mean)
    #         self._mean = new_mean
    #         self._second_part = None

    def _get_second_part(self):
        """
        Internal method that allows caching for second part of probability distribution function.
        If the value has already been calculated before, the cached value is returned, otherwise
        the value is initialised first.
        :return: Second part of pdf
        """
        if self._second_part is None:
            try:
                self._second_part = -1 / (2 * self.all_valid_variance)
            except ZeroDivisionError:
                self._second_part = 0
        return self._second_part

    @property
    def all_valid_variance(self):
        variance = self.variance
        # TODO: I maybe shouldn't check for bigger 0 here...
        return variance if variance is not None and variance > 0 else math.sqrt(self.count)

    def distance(self, value=None):
        """
        Check the current distance for a given value. The distance is not a distance in this way but
        more a similarity. If the value equals the mean, 0 is returned. For convenience, value being
        None or 0 get a distance of None, meaning, that the handling can be done externally.

        :param value: The value to check the distance for
        :return: Distance
        """
        if self.count > 0:
            if value is None or value == 0:
                return None
            if value == self.mean:
                return 0
            return 1 - math.exp(self._get_second_part() * (value - self.mean)**2)
        else:
            return float("inf")

    def object_distance(self, other=None):
        """
        Object distance is currently the ratio of the both means and the width of both variances.

        :param other: Other MeanVariance object to check
        :return: distance
        """
        try:
            return abs(self.mean - other.mean) / \
                   ((self.all_valid_variance + other.all_valid_variance) / 2)
        except ZeroDivisionError:
            return float("inf")

    @property
    def count(self):
        """
        Get the number of values that went into the statistics calculation.

        :return: Count of considered values
        """
        return self._count
