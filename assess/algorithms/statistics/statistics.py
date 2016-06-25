"""
Module implements possible methods to represent statistics that might be used for e.g. cluster
representatitives. Currently only MeanVariance is supported.
"""
import math


class MeanVariance(object):
    """
    Supported kind of statistic that can be utilised in SignatureCache to store signatures.
    The MeanVariance class offers a running mean and variance for inserted signatures and their
    assigned values.
    """
    def __init__(self, value=0.0):
        self._count = 1 if value != 0 else 0
        self._overall_count = 1 if value != 0 else 0
        self._mean = value
        self._variance = 0.0
        # remember for faster calculation
        self._first_part = None
        self._second_part = None

    def add(self, value=0.0):
        """
        Method to add a specific value for a given signature to its cache value.
        :param value: New value to add
        """
        self._overall_count += 1
        if value != 0:
            self._count += 1
            new_mean = self._mean + (value - self._mean) / float(self._count)
            self._variance += (value - self._mean) * (value - new_mean)
            self._mean = new_mean
            self._second_part = None

    @staticmethod
    def _get_first_part():
        """
        Internal method that allows caching for first part of probability distribution function.
        Currently the value is just a static one to directly map to a distance. 1 means, it is
        equal, 0 means it has a very far distance.
        curve(a*exp(-b*x*x), -3, 3)
        :return: First part of pdf
        """
        return 1
        # if self._first_part is None:
        #     try:
        #         self._first_part = 1 / (math.sqrt(2*math.pi*self._variance))
        #     except ZeroDivisionError:
        #         self._first_part = 0
        # return self._first_part

    def _get_second_part(self):
        """
        Internal method that allows caching for second part of probability distribution function.
        If the value has already been calculated before, the cached value is returned, otherwise
        the value is initialised first.
        :return: Second part of pdf
        """
        if self._second_part is None:
            try:
                self._second_part = -1 / (2*self._fixed_variance)
            except ZeroDivisionError:
                self._second_part = 0
        return self._second_part

    @property
    def _fixed_variance(self):
        return self._variance if self._variance > 0 else math.sqrt(self.count)

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
            if value == self._mean:
                return 0
            return 1 - math.exp(self._get_second_part() * (value - self._mean)**2)
        else:
            return float("inf")

    def object_distance(self, other=None):
        """
        Object distance is currently the ratio of the both means and the width of both variances.

        :param other: Other MeanVariance object to check
        :return: distance
        """
        return abs(self._mean - other._mean) / \
               (self._fixed_variance / 2 + (other._fixed_variance / 2))

    @property
    def count(self):
        """
        Get the number of values that went into the statistics calculation.

        :return: Count of considered values
        """
        return self._overall_count

    def update(self, statistics):
        """
        Method that updates the current MeanVariance object with the given MeanVariance object.
        Practically, a merging of both objects is performed.

        :param statistics: object which values are merged
        """
        self._overall_count += statistics.count
        count = self._count + statistics._count

        delta = statistics._mean - self._mean
        self._mean += delta * (statistics._count / count)
        self._variance += statistics._variance + \
                          (delta * delta * (self._count * statistics._count / count))
        self._count = count
