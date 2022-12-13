import sys
from django.test import TestCase
from testfixtures import log_capture
from bear_applications.models import Architecture

sys.path.insert(0, "../../scripts")
from architecture import set_visibility


class ArchitectureTestCase(TestCase):
    """
    Test the architecture.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    def test_mark_hidden_when_already_hidden(self, log):
        """
        Test mark_hidden on an already hidden arch
        """
        arch = Architecture.objects.get(name="BB-Hidden-Arch")
        self.assertTrue(arch.hidden)
        set_visibility(arch=arch, hidden=True)
        log.check(("architecture", "INFO", "Architecture Hidden marked as hidden"))
        self.assertTrue(arch.hidden)

    @log_capture()
    def test_mark_hidden(self, log):
        """
        Test mark_hidden
        """
        arch = Architecture.objects.get(name="EL7-p9")
        self.assertFalse(arch.hidden)
        set_visibility(arch=arch, hidden=True)
        log.check(("architecture", "INFO", "Architecture EL7-power9 marked as hidden"))
        self.assertTrue(arch.hidden)

    @log_capture()
    def test_mark_visible_when_already_hidden(self, log):
        """
        Test mark_visible on an already visible arch
        """
        arch = Architecture.objects.get(name="EL7-p9")
        self.assertFalse(arch.hidden)
        set_visibility(arch=arch, hidden=False)
        log.check(("architecture", "INFO", "Architecture EL7-power9 marked as visible"))
        self.assertFalse(arch.hidden)

    @log_capture()
    def test_mark_visible(self, log):
        """
        Test mark_visible
        """
        arch = Architecture.objects.get(name="BB-Hidden-Arch")
        self.assertTrue(arch.hidden)
        set_visibility(arch=arch, hidden=False)
        log.check(("architecture", "INFO", "Architecture Hidden marked as visible"))
        self.assertFalse(arch.hidden)
