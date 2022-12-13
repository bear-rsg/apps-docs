import sys
from django.test import TestCase
from testfixtures import log_capture

sys.path.insert(0, "../../scripts")
from add_application_version import add_appver


class AddApplicationVersionTestCase(TestCase):
    """
    Test the add_application_version.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    def test_add_appver_moduleload_abort(self, log):
        """
        Test add_appver with 'module load' in the module
        """
        with self.assertRaises(SystemExit) as cm:
            add_appver("app", "ver", "module load modload", "home", "desc", "bav")
        self.assertEqual(cm.exception.code, 1)
        log.check(("functions", "ERROR", "Please don't include 'module load' in your module load command"))

    @log_capture()
    def test_add_appver(self, log):
        """
        Test add_appver
        """
        add_appver(
            "Python",
            "3.8.2-GCCcore-9.3.0",
            "Python/3.8.2-GCCcore-9.3.0",
            "https://test.com",
            "Here we describe",
            "219a",
        )
        log.check(
            ("functions", "INFO", "Uploading Python/3.8.2-GCCcore-9.3.0"),
            ("functions", "INFO", "Application Python already exists"),
            ("functions", "INFO", "Created bearappsversion family 219a"),
            ("functions", "INFO", "Created version 3.8.2-GCCcore-9.3.0"),
            ("functions", "INFO", "Set as current version"),
        )
