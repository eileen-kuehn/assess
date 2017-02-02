"""
Module implements possible methods to represent statistics that might be used for e.g. cluster
representatitives. Currently only MeanVariance is supported.
"""
from __future__ import division
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

    .. describe:: mean

       Returns the mean representation of the given statistics.

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

    def count(self, value=None):
        """
        If value is not given, returns the count of objects that went into statistics. Otherwise
        the count for given value is returned.

        :param value: Value to check the count for
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

    @classmethod
    def mean(cls, values):
        """
        Returns the average representation of given statistics values by considering encapsulated
        statistics as well as the length of values.

        :param values: The statistics values to be averaged.
        :return: New statistics object representing the given values.
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
        self.variance = 0.0
        if value is not None:
            self.add(value=value)

    def __iadd__(self, statistics):
        """
        Method that updates the current MeanVariance object with the given MeanVariance object.
        Practically, a merging of both objects is performed.

        :param statistics: object which values are merged
        """
        variance_a = self.variance * (self._count - 1)
        variance_b = statistics.variance * (statistics.count - 1)

        count = self._count + statistics.count
        delta = statistics.mean - self._mean

        self._mean += delta * (statistics.count / count)
        self.variance = variance_a + variance_b + (delta * delta * (self._count * statistics.count) / count)
        self._count = count
        try:
            self.variance /= self._count - 1
        except ZeroDivisionError:
            self.variance = 0.0
        return self

    def add(self, value=.0):
        if self._count > 1:
            self.variance *= self._count - 1
        self._count += 1
        delta = value - self._mean
        self._mean += delta / self._count
        self.variance += delta * (value - self._mean)
        if self._count < 2:
            self.variance = 0
        else:
            self.variance /= self._count - 1

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
        Returns the distance between the two objects.

        :param other: Other MeanVariance object to check
        :return: distance
        """
        return self._height_distance(other)

    @property
    def count(self):
        """
        Get the number of values that went into the statistics calculation.

        :return: Count of considered values
        """
        return self._count

    def _mean_distance(self, other=None):
        """
        Object distance is currently the ratio of the both means and the width of both variances.

        :param other: Other MeanVariance object to check
        :return: distance
        """
        try:
            return abs(self.mean - other.mean) / \
                   ((self.all_valid_variance + other.all_valid_variance) / 2.0)
        except ZeroDivisionError:
            return float("inf")

    def _height_distance(self, other=None):
        merged = self._merge_pdfs(self, other)
        left_pdf = self._pdf(self.mean, self.mean, variance=self.all_valid_variance) * self.count
        right_pdf = self._pdf(other.mean, other.mean, variance=other.all_valid_variance) * other.count
        merged_pdf_left = self._pdf(self.mean, merged["mean"], variance=merged["variance"]) * merged["count"]
        merged_pdf_right = self._pdf(other.mean, merged["mean"], variance=merged["variance"]) * merged["count"]
        try:
            left_distance = left_pdf / merged_pdf_left
            right_distance = right_pdf / merged_pdf_right
        except ZeroDivisionError:
            return 0
        return min(left_distance, right_distance)

    @staticmethod
    def _merge_pdfs(first, other):
        variance_a = first.all_valid_variance * (first.count - 1)
        variance_b = other.all_valid_variance * (other.count - 1)

        count = first.count + other.count
        delta = other.mean - first.mean
        mean = first.mean + delta * (other.count / count)
        variance = variance_a + variance_b + (delta * delta * (count * other.count / count))
        return {"count": count, "mean": mean, "variance": variance/(count - 1)}

    def _pdf(self, x_value, mean, variance=None):
        return 1 / math.sqrt(2 * variance * math.pi) * math.exp(
            -(x_value - mean)**2 / (2.0 * float(variance)))

    def height(self, x_value):
        return self._pdf(x_value, self.mean, self.all_valid_variance) * self.count

    def __repr__(self):
        return '%s(mean=%s,variance=%s,count=%s)' % (self.__class__.__name__, self.mean, self.variance, self.count)
