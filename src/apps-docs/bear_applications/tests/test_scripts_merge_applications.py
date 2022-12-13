import os
import sys
from django.test import TestCase
from testfixtures import log_capture
from unittest.mock import patch

sys.path.insert(0, "../../scripts")
from merge_applications import rename_application


class MergeApplicationsTestCase(TestCase):
    """
    Test the merge_applications.py script
    """

    fixtures = ["db.json"]

    @patch.dict("os.environ", {"USER": "me"})
    @log_capture()
    def test_rename_application(self, log):
        """
        Test rename_application
        """
        rename_application(oldname="MATLAB", newname="TensorFlow")
        log.check(
            ("merge_applications", "INFO", "moved 2017a from MATLAB to TensorFlow"),
            ("merge_applications", "INFO", "moved 2017b from MATLAB to TensorFlow"),
            ("merge_applications", "INFO", "moved 2014a from MATLAB to TensorFlow"),
            ("merge_applications", "INFO", "moved R2018b from MATLAB to TensorFlow"),
            ("merge_applications", "INFO", "delete R2018b as MATLAB current version"),
            ("merge_applications", "INFO", "MATLAB hidden, with reason merged MATLAB into TensorFlow"),
        )

    @patch.dict("os.environ", {"USER": "me"})
    @log_capture()
    def test_rename_application_with_no_user(self, log):
        """
        Test rename_application with no USER (env variable) defined
        """
        with patch.dict("os.environ"):
            del os.environ["USER"]
            with self.assertRaises(SystemExit) as cm:
                rename_application(oldname="MATLAB", newname="TensorFlow")
            self.assertEqual(cm.exception.code, 1)
        log.check(("functions", "ERROR", "Unable to identify user from environment (looked for USER in env)"))
