import sys
from django.test import TestCase
from testfixtures import log_capture
from unittest.mock import patch, mock_open, Mock
from bear_applications.models import Version

sys.path.insert(0, "../../scripts")
from add_module_info import add_module

FAKE_MODULE_FILE1 = """module-whatis {Homepage: https://test.com }
module-whatis {Description: A new piece of software }
module-whatis {Extensions: A-4,B-3 }
module-whatis {Compatible modules: MATLAB/2014a }
module load MATLAB/R2018b
module load TensorFlow/1.13.1-fosscuda-2018b-Python-3.6.6"""

FAKE_MODULE_FILE2 = """module-whatis {Homepage: https://test.com }
module-whatis {Description: A new piece of software }
module-whatis {Extensions: A-4,B-3 }
if { ![ is-loaded PyTorch/1.2.0-fosscuda-2019a-Python-3.7.2 ] } {
    module load PyTorch/1.2.0-fosscuda-2019a-Python-3.7.2
}
NOTADEP = "module load not/a-dep"
"""


class AddModuleInfoTestCase(TestCase):
    """
    Test the add_module_info.py script
    """

    fixtures = ["db.json"]

    @log_capture()
    @patch("os.stat")
    @patch("builtins.open", new_callable=mock_open, read_data="blah")
    def test_add_module_no_regex_matches(self, mock_file, os_stat, log):
        """
        Test add_module when we do not match for homepage, description, etc.
        """
        os_stat.return_value = Mock(st_ctime=1530346690, st_mtime=1530347690)
        with self.assertRaises(SystemExit) as cm:
            add_module("/no/file", False)
        self.assertEqual(cm.exception.code, 1)
        log.check_present(
            ("root", "INFO", "Couldn't get home"),
            ("root", "INFO", "Couldn't get desc"),
            ("root", "INFO", "Couldn't get ext"),
            (
                "functions",
                "ERROR",
                "Unable to upload data for /no/file. Error: upload_data() missing 7 required positional arguments: "
                "'name', 'version', 'arch', 'bav_family', 'module_load', 'home', and 'desc'",
            ),
        )

    @log_capture()
    @patch("os.stat")
    @patch("builtins.open", new_callable=mock_open, read_data=FAKE_MODULE_FILE1)
    def test_add_module_regex_matches(self, mock_file, os_stat, log):
        """
        Test add_module when we match homepage, description, etc.
        """
        os_stat.return_value = Mock(st_ctime=1530346690, st_mtime=1530347690)
        add_module("/rds/bear-apps/2020a/EL7-cascadelake/modules/all/Cardinal/2.6.0-foss-2020a-R-4.0.0", False)
        log.check_present(
            ("functions", "INFO", "Uploading Cardinal/2.6.0-foss-2020a-R-4.0.0"),
            ("functions", "INFO", "Created application Cardinal"),
            ("functions", "INFO", "Created architecture EL7-cascadelake"),
            ("functions", "INFO", "Created bearappsversion family 2020a"),
            ("functions", "INFO", "Created version 2.6.0-foss-2020a-R-4.0.0"),
            ("functions", "INFO", "Set extension info in a paragraph"),
            ("functions", "INFO", "Linked 2.6.0-foss-2020a-R-4.0.0, EL7-cascadelake and 2020a"),
            ("functions", "INFO", "Set as current version"),
            ("functions", "INFO", "Set MATLAB/R2018b as dependency"),
            ("functions", "INFO", "Set MATLAB/2014a as dependency"),
        )

    @log_capture()
    @patch("os.stat")
    @patch("builtins.open", new_callable=mock_open, read_data=FAKE_MODULE_FILE1)
    def test_add_module_skip_deps(self, mock_file, os_stat, log):
        """
        Test add_module with skip deps
        """
        os_stat.return_value = Mock(st_ctime=1530346690, st_mtime=1530347690)
        add_module("/rds/bear-apps/2020a/EL7-cascadelake/modules/all/Cardinal/2.6.0-foss-2020a-R-4.0.0", True)
        log.check(
            ("functions", "INFO", "Uploading Cardinal/2.6.0-foss-2020a-R-4.0.0"),
            ("functions", "INFO", "Created application Cardinal"),
            ("functions", "INFO", "Created architecture EL7-cascadelake"),
            ("functions", "INFO", "Created bearappsversion family 2020a"),
            ("functions", "INFO", "Created version 2.6.0-foss-2020a-R-4.0.0"),
            ("functions", "INFO", "Set extension info in a paragraph"),
            ("functions", "INFO", "Linked 2.6.0-foss-2020a-R-4.0.0, EL7-cascadelake and 2020a"),
            ("functions", "INFO", "Set as current version"),
        )

    @log_capture()
    @patch("os.stat")
    @patch("builtins.open", new_callable=mock_open, read_data=FAKE_MODULE_FILE2)
    def test_add_module_with_deps(self, mock_file, os_stat, log):
        """
        Test add_module with deps
        """
        add_module("/rds/bear-apps/2020a/EL7-cascadelake/modules/all/TensorFlow/1.13.1-fosscuda-2018b-Python-3.8.2",
                   False)
        log.check_present(
            ('functions', 'INFO', 'Set PyTorch/1.2.0-fosscuda-2019a-Python-3.7.2 as dependency')
        )
        app = Version.objects.get(version='1.13.1-fosscuda-2018b-Python-3.8.2', application__name='TensorFlow')
        self.assertEqual(app.dependencies.count(), 1)
