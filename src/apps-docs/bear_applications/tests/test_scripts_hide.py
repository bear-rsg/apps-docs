import os
import sys
from django.test import TestCase
from testfixtures import log_capture
from unittest.mock import patch
from bear_applications.models import Application, Version

sys.path.insert(0, "../../scripts")
from hide import _hide_obj


class HideTestCase(TestCase):
    """
    Test the hide.py script
    """

    fixtures = ["db.json"]

    @patch.dict("os.environ", {"USER": "me"})
    @log_capture()
    def test_hide_obj_with_application(self, log):
        """
        Test _hide_obj with an application
        """
        application = Application.objects.get(name="MATLAB")
        _hide_obj(obj_to_hide=application, reason="Bye Bye")
        log.check(("hide", "INFO", "Application MATLAB hidden, with reason Bye Bye"))

    @patch.dict("os.environ", {"USER": "me"})
    @log_capture()
    def test_hide_obj_with_version(self, log):
        """
        Test _hide_obj with an version
        """
        version = Version.objects.get(version="R2018b", application__name="MATLAB")
        _hide_obj(obj_to_hide=version, reason="Bye Bye")
        log.check(("hide", "INFO", "Version R2018b of MATLAB hidden, with reason Bye Bye"))

    @patch.dict("os.environ", {"USER": "me"})
    @log_capture()
    def test_hide_obj_with_no_user(self, log):
        """
        Test _hide_obj with no USER (env variable) defined
        """
        with patch.dict("os.environ"):
            del os.environ["USER"]
            with self.assertRaises(SystemExit) as cm:
                _hide_obj(obj_to_hide="bar", reason="Bye Bye")
            self.assertEqual(cm.exception.code, 1)
        log.check(("functions", "ERROR", "Unable to identify user from environment (looked for USER in env)"))
