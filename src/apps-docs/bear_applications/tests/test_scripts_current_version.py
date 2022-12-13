import sys
from django.test import TestCase
from unittest.mock import MagicMock
from testfixtures import log_capture
from bear_applications.models import CurrentVersion, Version

sys.path.insert(0, "../../scripts")
from current_version import set_current_version


class SetCurrentVersionTestCase(TestCase):
    """
    Test the set_current_version.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    def test_rename_version(self, log):
        """
        Test rename_version
        """
        ver = Version.objects.get(version="2014a", application__name="MATLAB")
        cv = CurrentVersion.objects.get(application=ver.application)
        self.assertEqual(cv.version.version, "R2018b")
        args = MagicMock()
        args.application = "MATLAB"
        args.version = "2014a"
        set_current_version(args)
        log.check(
            ("current_version", "INFO", "Unset version R2018b"),
            ("current_version", "INFO", "2014a set as current version for MATLAB"),
        )
        cv = CurrentVersion.objects.get(application=ver.application)
        self.assertEqual(cv.version.version, "2014a")
