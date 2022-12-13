import sys
from django.test import TestCase
from testfixtures import log_capture
from bear_applications.models import Version

sys.path.insert(0, "../../scripts")
from version import rename_version, change_module_load, change_app_sort_order


class VersionTestCase(TestCase):
    """
    Test the version.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    def test_rename_version(self, log):
        """
        Test rename_version
        """
        ver = Version.objects.get(version="2014a", application__name="MATLAB")
        self.assertEqual(ver.version, "2014a")
        rename_version(version=ver, newname="Penguins")
        log.check(("version", "INFO", "Renamed MATLAB 2014a to Penguins"))
        self.assertEqual(ver.version, "Penguins")

    @log_capture()
    def test_change_module_load(self, log):
        """
        Test change_module_load
        """
        ver = Version.objects.get(version="2014a", application__name="MATLAB")
        self.assertEqual(ver.module_load, "apps/matlab/2014a")
        change_module_load(version=ver, module_load="Penguins")
        log.check(("version", "INFO", "Module load for MATLAB 2014a changed from apps/matlab/2014a to Penguins"))
        self.assertEqual(ver.module_load, "Penguins")

    @log_capture()
    def test_change_app_sort_order(self, log):
        """
        Test change_app_sort_order
        """
        ver = Version.objects.get(version="2014a", application__name="MATLAB")
        self.assertEqual(ver.app_sort_order, 0)
        change_app_sort_order(version=ver, order=-10)
        log.check(("version", "INFO", "For MATLAB / 2014a the sort order has changed from 0 to -10"))
        self.assertEqual(ver.app_sort_order, -10)
