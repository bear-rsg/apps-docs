import sys
from datetime import datetime
from django.test import TestCase
from testfixtures import log_capture
from bear_applications.models import Application, CurrentVersion, Version

sys.path.insert(0, "../../scripts")
from openfoam import OPENFOAM_APPLICATION_NAME, OPENFOAM_INFORMATION_PAGE, move_new_version


class OpenfoamTestCase(TestCase):
    """
    Test the openfoam.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    def test_move_new_version(self, log):
        """
        Test move_new_version
        """
        openfoam = Application.objects.get(name=OPENFOAM_APPLICATION_NAME)
        Version.objects.create(
            version="New",
            created=datetime.now().astimezone(),
            modified=datetime.now().astimezone(),
            application=openfoam,
        )
        Version.objects.create(
            version=OPENFOAM_INFORMATION_PAGE,
            created=datetime.now().astimezone(),
            modified=datetime.now().astimezone(),
            application=openfoam,
        )

        move_new_version(target_openfoam="OpenFOAM Real", version="New", set_as_current=True)
        log.check(
            ("openfoam", "INFO", "Moved New to OpenFOAM Real"),
            ("current_version", "INFO", "New set as current version for OpenFOAM Real"),
            ("openfoam", "INFO", "Set New as current version for OpenFOAM Real"),
            ("current_version", "INFO", "Information Page set as current version for OpenFOAM"),
            ("openfoam", "INFO", "Reset OpenFOAM Information Page as current version"),
        )

        openfoam_cv = CurrentVersion.objects.get(application__name=OPENFOAM_APPLICATION_NAME)
        openfoam_real_cv = CurrentVersion.objects.get(application__name="OpenFOAM Real")
        self.assertEqual(openfoam_cv.version.version, OPENFOAM_INFORMATION_PAGE)
        self.assertEqual(Version.objects.filter(application=openfoam).count(), 1)
        self.assertEqual(openfoam_real_cv.version.version, "New")
