import sys
from django.test import TestCase
from testfixtures import log_capture
from bear_applications.models import BearAppsVersion

sys.path.insert(0, "../../scripts")
from bear_apps_version import (
    mark_deprecated,
    mark_not_deprecated,
    mark_auto_loaded,
    mark_not_auto_loaded,
)


class BearAppsVersionTestCase(TestCase):
    """
    Test the bear_apps_version.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    def test_mark_deprecated_when_already_deprecated(self, log):
        """
        Test mark_deprecated on an already deprecated bav
        """
        bav = BearAppsVersion.objects.get(name="2017a")
        self.assertTrue(bav.deprecated)
        mark_deprecated(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2017a marked as deprecated",))
        self.assertTrue(bav.deprecated)

    @log_capture()
    def test_mark_deprecated(self, log):
        """
        Test mark_deprecated
        """
        bav = BearAppsVersion.objects.get(name="2019a")
        self.assertFalse(bav.deprecated)
        mark_deprecated(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2019a marked as deprecated",))
        self.assertTrue(bav.deprecated)

    @log_capture()
    def test_mark_not_deprecated_when_already_not_deprecated(self, log):
        """
        Test mark_not_deprecated on an already not deprecated bav
        """
        bav = BearAppsVersion.objects.get(name="2019a")
        self.assertFalse(bav.deprecated)
        mark_not_deprecated(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2019a marked as not deprecated",))
        self.assertFalse(bav.deprecated)

    @log_capture()
    def test_mark_not_deprecated(self, log):
        """
        Test mark_not_deprecated
        """
        bav = BearAppsVersion.objects.get(name="2017a")
        self.assertTrue(bav.deprecated)
        mark_not_deprecated(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2017a marked as not deprecated",))
        self.assertFalse(bav.deprecated)

    @log_capture()
    def test_mark_auto_loaded_when_already_auto_loaded(self, log):
        """
        Test mark_auto_loaded on an already auto_loaded bav
        """
        bav = BearAppsVersion.objects.get(name="2019a")
        self.assertTrue(bav.auto_loaded)
        mark_auto_loaded(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2019a marked as loaded by default",))
        self.assertTrue(bav.auto_loaded)

    @log_capture()
    def test_mark_auto_loaded(self, log):
        """
        Test mark_auto_loaded
        """
        bav = BearAppsVersion.objects.get(name="2018b-1")
        self.assertFalse(bav.auto_loaded)
        mark_auto_loaded(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2018b marked as loaded by default",))
        self.assertTrue(bav.auto_loaded)

    @log_capture()
    def test_mark_not_auto_loaded_when_already_not_auto_loaded(self, log):
        """
        Test mark_not_auto_loaded on an already not auto_loaded bav
        """
        bav = BearAppsVersion.objects.get(name="2018b-1")
        self.assertFalse(bav.auto_loaded)
        mark_not_auto_loaded(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2018b marked as not loaded by default",))
        self.assertFalse(bav.auto_loaded)

    @log_capture()
    def test_mark_not_auto_loaded(self, log):
        """
        Test mark_not_auto_loaded
        """
        bav = BearAppsVersion.objects.get(name="2019a")
        self.assertTrue(bav.auto_loaded)
        mark_not_auto_loaded(bear_application_version=bav)
        log.check(("bear_apps_version", "INFO", "BEAR Application Version 2019a marked as not loaded by default",))
        self.assertFalse(bav.auto_loaded)
