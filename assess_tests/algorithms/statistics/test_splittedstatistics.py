import unittest
import random

from assess.algorithms.statistics.splittedstatistics import SplittedStatistics
from assess.algorithms.statistics.statistics import MeanVariance


class TestSplittedStatistics(unittest.TestCase):
    def test_zero_handling(self):
        statistics = SplittedStatistics(statistics_type=MeanVariance)
        statistics.add(value=0)
        for statistic in statistics._statistics:
            print "mean: %s, variance: %s (%s), count: %s" % (statistic.mean, statistic.variance, statistic.all_valid_variance, statistic.count)
        self.assertEqual(statistics.distance(value=1), float("inf"))
        # distance should stay the same, also with more 0 values
        for _ in xrange(1000):
            statistics.add(value=0)
        for statistic in statistics._statistics:
            print "mean: %s, variance: %s (%s), count: %s" % (statistic.mean, statistic.variance, statistic.all_valid_variance, statistic.count)
        self.assertEqual(statistics.distance(value=1), float("inf"))

    def test_all_valid_variance(self):
        statistics = SplittedStatistics(statistics_type=MeanVariance)
        statistics.add(value=0)
        self.assertEqual(statistics._statistics[0].all_valid_variance, 1)
        for _ in xrange(1000):
            statistics.add(value=0)
        self.assertEqual(statistics._statistics[0].all_valid_variance, 0)

    def test_adding_with_zero(self):
        statistics = SplittedStatistics(statistics_type=MeanVariance)
        self.assertEqual(len(statistics._statistics), 0)
        statistics.add(value=0)
        self.assertEqual(len(statistics._statistics), 1)
        statistics.add(value=1)
        self.assertEqual(len(statistics._statistics), 2)

        statistics = SplittedStatistics(statistics_type=MeanVariance)
        for _ in xrange(1000):
            statistics.add(value=0)
        self.assertEqual(len(statistics._statistics), 1)
        statistics.add(value=1)
        self.assertEqual(len(statistics._statistics), 2)

    def test_order(self):
        statistics = SplittedStatistics(statistics_type=MeanVariance)
        random.seed(1234)
        for _ in xrange(1000):
            value = random.randint(0, 10000)
            statistics.add(value)
        last = -float("inf")
        for statistic in statistics._statistics:
            self.assertTrue(statistic.mean > last)
            last = statistic.mean

