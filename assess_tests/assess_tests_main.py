import unittest

from assess_tests.algorithms.signatures.test_signatures import TestSignatureFunctionalities
from assess_tests.algorithms.test_incrementaldistancealgorithm import TestIncrementalDistanceAlgorithmFunctionality
from assess_tests.algorithms.test_treeinclusionalgorithm import TestTreeInclusionDistanceAlgorithm

from assess_tests.events.test_events import TestEventFunctionality


def test_assess():
    signature_suite = unittest.TestLoader().loadTestsFromTestCase(TestSignatureFunctionalities)
    incremental_algorithm_suite = unittest.TestLoader().loadTestsFromTestCase(
            TestIncrementalDistanceAlgorithmFunctionality
    )
    inclusion_algorithm_suite = unittest.TestLoader().loadTestsFromTestCase(TestTreeInclusionDistanceAlgorithm)
    event_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFunctionality)

    alltests = unittest.TestSuite(
            [event_suite, signature_suite, incremental_algorithm_suite, inclusion_algorithm_suite]
    )
    unittest.TextTestRunner(verbosity=2).run(alltests)

if __name__ == '__main__':
    test_assess()
