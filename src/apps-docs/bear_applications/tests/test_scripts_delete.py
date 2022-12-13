import sys
from django.test import TestCase
from unittest.mock import patch
from io import StringIO
from testfixtures import log_capture
from bear_applications.models import Version

sys.path.insert(0, "../../scripts")
from delete import delete


class DeleteTestCase(TestCase):
    """
    Test the delete.py script
    """

    fixtures = ["db.json"]

    def _count_matlab_versions(self):
        """
        How many versions of MATLAB are there?
        """
        return Version.objects.filter(application__name="MATLAB").count()

    @log_capture()
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="y")
    def test_delete_application(self, input, mock_stdout, log):
        """
        Test deleting an application
        """
        delete(application="MATLAB")
        log.check(
            ("delete", "INFO", "2017a deleted"),
            ("delete", "INFO", "2017b deleted"),
            ("delete", "INFO", "2014a deleted"),
            ("delete", "INFO", "R2018b deleted"),
            ("delete", "INFO", "MATLAB deleted"),
        )
        self.assertEqual(mock_stdout.getvalue(), "WARNING: This will permanently delete MATLAB (all versions)\n")
        self.assertEqual(0, self._count_matlab_versions())

    @log_capture()
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="y")
    def test_delete_version(self, input, mock_stdout, log):
        """
        Test deleting a version of an application
        """
        num_matlab = self._count_matlab_versions()
        delete(application="MATLAB", version="2017b")
        log.check(("delete", "INFO", "2017b deleted"))
        self.assertEqual(mock_stdout.getvalue(), "WARNING: This will permanently delete MATLAB (2017b)\n")
        self.assertEqual(num_matlab - 1, self._count_matlab_versions())

    @log_capture()
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="N")
    def test_delete_abort(self, input, mock_stdout, log):
        """
        Test abort of deletion
        """
        num_matlab = self._count_matlab_versions()
        delete(application="MATLAB")
        log.check(("delete", "INFO", "Aborting"))
        self.assertEqual(mock_stdout.getvalue(), "WARNING: This will permanently delete MATLAB (all versions)\n")
        self.assertEqual(num_matlab, self._count_matlab_versions())
