import pytz
from datetime import datetime
from django.test import TestCase
from testfixtures import log_capture
from bear_applications.models import Application, Version, BearAppsVersion, Architecture, Link

import sys
sys.path.insert(0, "../../scripts")
from functions import abort, get_application, set_dependencies, set_up_logging, upload_data, _parse_ext_list_to_html


class FunctionsTestCase(TestCase):
    """
    Test the functions.py script
    """
    fixtures = ['db.json']

    @log_capture()
    def test_abort(self, log):
        """
        Test the abort function
        """
        with self.assertRaises(SystemExit) as cm:
            abort("Hello world!")
        self.assertEqual(cm.exception.code, 1)
        log.check(('functions', 'ERROR', 'Hello world!'))

    @log_capture()
    def test_get_application_does_not_exist(self, log):
        """
        Test that we get an error with an application that does not exist
        """
        with self.assertRaises(SystemExit) as cm:
            get_application(name='jfwjoweweo')
        self.assertEqual(cm.exception.code, 1)
        log.check(('functions', 'ERROR', "Can't find application jfwjoweweo"))

    def test_get_application_exists_but_no_version(self):
        """
        Test that we find an application that exists
        """
        app, ver = get_application(name='TensorFlow')
        self.assertEqual(app.name, 'TensorFlow')
        self.assertEqual(ver, None)

    @log_capture()
    def test_get_application_exists_but_version_does_not_exist(self, log):
        """
        Test that we get an error with an application that exists but a version that does not exist
        """
        with self.assertRaises(SystemExit) as cm:
            get_application(name='TensorFlow', version='jfwjowewe')
        self.assertEqual(cm.exception.code, 1)
        log.check(('functions', 'ERROR', "Can't find TensorFlow version jfwjowewe"))

    def test_get_application_exists(self):
        """
        Test that we find a vesion of an application that exists
        """
        app, ver = get_application(name='TensorFlow', version='1.13.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(app.name, 'TensorFlow')
        self.assertEqual(ver.version, '1.13.1-fosscuda-2018b-Python-3.6.6')

    @log_capture()
    def test_set_up_logging_nondebug(self, log):
        """
        Test logging setup - nondebug
        """
        import logging
        set_up_logging(False)
        logger = logging.getLogger(__name__)
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)
        self.assertEqual(logger.root.handlers[1].formatter._fmt, '[%(levelname)s] %(message)s')

    @log_capture()
    def test_set_up_logging_debug(self, log):
        """
        Test logging setup - debug
        """
        import logging
        set_up_logging(True)
        logger = logging.getLogger(__name__)
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)
        self.assertEqual(logger.root.handlers[1].formatter._fmt, '[%(levelname)s] %(message)s')

    def test_add_dependency(self):
        """
        Test the adding of a known dependency
        """
        _, ver = get_application(name='TensorFlow', version='1.13.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(ver.dependencies.count(), 0)
        set_dependencies(ver, ['Python/2.7.12-foss-2012a'])
        self.assertEqual(ver.dependencies.count(), 1)

    @log_capture()
    def test_add_unknown_dependency(self, log):
        """
        Test the adding of an unknown dependency
        """
        _, ver = get_application(name='TensorFlow', version='1.13.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(ver.dependencies.count(), 0)
        with self.assertRaises(SystemExit) as cm:
            set_dependencies(ver, ['Python/2016a'])
        self.assertEqual(cm.exception.code, 1)
        log.check_present(('functions', 'ERROR', "Can't find Python version 2016a"))
        self.assertEqual(ver.dependencies.count(), 0)

    def test_replace_dependencies(self):
        """
        Test setting dependencies for something that already has some set
        """
        _, ver = get_application(name='TensorFlow', version='1.13.1-foss-2018b-Python-3.6.6')
        self.assertEqual(ver.dependencies.count(), 2)
        self.assertEqual(ver.sorted_dependencies[0].version, '1.2.0-fosscuda-2019a-Python-3.7.2')
        self.assertEqual(ver.sorted_dependencies[1].version, '1.13.1-fosscuda-2018b-Python-3.6.6')
        set_dependencies(ver, ['Python/2.7.12-foss-2012a'])
        self.assertEqual(ver.dependencies.count(), 1)
        self.assertEqual(ver.sorted_dependencies[0].version, '2.7.12-foss-2012a')

    def test_one_splittable_ext(self):
        """
        Test one splittable extension
        """
        output = _parse_ext_list_to_html("one-1.1")
        self.assertEqual(output, "<ul><li>one 1.1</li></ul>")

    def test_one_unsplittable_ext(self):
        """
        Test one unsplittable extension
        """
        output = _parse_ext_list_to_html("one-1.1-1")
        self.assertEqual(output, "<ul><li>one-1.1-1</li></ul>")

    def test_multiple_mixed_exts(self):
        """
        Test multiple extensions
        """
        output = _parse_ext_list_to_html("one-1.1-1,two-2.2,three-3.4.2")
        self.assertEqual(output, "<ul><li>one-1.1-1</li><li>two 2.2</li><li>three 3.4.2</li></ul>")

    @log_capture()
    def test_upload_data_existing(self, log):
        """
        Test upload_data with existing information, nothing should be created
        """
        num_apps = Application.objects.all().count()
        num_vers = Version.objects.all().count()
        num_bavs = BearAppsVersion.objects.all().count()
        num_arch = Architecture.objects.all().count()

        time = datetime.utcnow().replace(tzinfo=pytz.utc)
        upload_data("MATLAB", "2017b", "EL7-haswell", "2019a", "MATLAB/2017b", "https://test.com", "MATLAB", time, time)
        log.check(
            ('functions', 'INFO', 'Uploading MATLAB/2017b'),
            ('functions', 'INFO', 'Application MATLAB already exists'),
            ('functions', 'INFO', 'Version 2017b already exists'),
        )

        self.assertEqual(num_apps, Application.objects.all().count())
        self.assertEqual(num_vers, Version.objects.all().count())
        self.assertEqual(num_bavs, BearAppsVersion.objects.all().count())
        self.assertEqual(num_arch, Architecture.objects.all().count())

    @log_capture()
    def test_upload_data_new(self, log):
        """
        Test upload_data with new information, that should create all the relevant items
        """
        num_apps = Application.objects.all().count()
        num_vers = Version.objects.all().count()
        num_bavs = BearAppsVersion.objects.all().count()
        num_arch = Architecture.objects.all().count()

        time = datetime.utcnow().replace(tzinfo=pytz.utc)
        upload_data("New", "new", "new", "new", "new", "new", "new", time, time, ext="A-4,B-5", deps=["MATLAB/2017b"])
        log.check_present(
            ('functions', 'INFO', 'Uploading New/new'),
            ('functions', 'INFO', 'Created application New'),
            ('functions', 'INFO', 'Created architecture new'),
            ('functions', 'INFO', 'Created bearappsversion family new'),
            ('functions', 'INFO', 'Created version new'),
            ('functions', 'INFO', 'Set extension info in a paragraph'),
            ('functions', 'INFO', 'Linked new, new and new'),
            ('functions', 'INFO', 'Set as current version'),
            ('functions', 'INFO', 'Set MATLAB/2017b as dependency'),
        )

        self.assertEqual(num_apps + 1, Application.objects.all().count())
        self.assertEqual(num_vers + 1, Version.objects.all().count())
        self.assertEqual(num_bavs + 1, BearAppsVersion.objects.all().count())
        self.assertEqual(num_arch + 1, Architecture.objects.all().count())

        new_link = Link.objects.get(version__version="new", version__application__name="New",
                                    bearappsversion__name="new", architecture__name="new")
        self.assertEqual(new_link.version.application.description, "new")
