import sys
from django.test import TestCase
from testfixtures import log_capture

sys.path.insert(0, "../../scripts")
from count import counts


class CountTestCase(TestCase):
    """
    Test the count.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    def test_counts(self, log):
        """
        Test counts
        """
        counts()
        log.check(
            ("count", "INFO", "All counts are for unhidden items"),
            ("count", "INFO", "Application count: 2"),
            ("count", "INFO", "Version count: 10"),
            ("count", "INFO", "Combo count: 10"),
        )
