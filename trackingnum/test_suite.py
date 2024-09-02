import unittest
from django.test import TestCase
from .tests import TrackingNumberConcurrentTest, TrackingNumberAPITestCase  

# Create a test suite
def suite():
    suite = unittest.TestSuite()
    # Add test cases to the suite
    suite.addTest(unittest.makeSuite(TrackingNumberAPITestCase))
    suite.addTest(unittest.makeSuite(TrackingNumberConcurrentTest))
    return suite

if __name__ == "__main__":
    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
