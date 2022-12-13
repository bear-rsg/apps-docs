import os
from django.test import TestCase
from django.utils.lorem_ipsum import paragraphs
from testfixtures import log_capture, tempdir
from bear_applications.models import Application

import sys
sys.path.insert(0, "../../scripts")
from application import change_description, change_more_information, get_description, rename_application, show_order


class ApplicationTestCase(TestCase):
    """
    Test the application.py script
    """

    fixtures = ['db.json']

    @log_capture()
    def test_sort_order(self, log):
        """
        Test the sort_order output
        """
        tf = Application.objects.get(name='TensorFlow')
        show_order(application=tf)
        log.check(
            ('application', 'INFO', 'Application: TensorFlow'),
            ('application', 'INFO', '    1.10.1-foss-2017a-Python-3.6.6 (3)'),
            ('application', 'INFO', '    1.10.1-fosscuda-2018b-Python-3.6.6 (0)'),
            ('application', 'INFO', '    1.10.1-foss-2018b-Python-3.6.6 (0)'),
            ('application', 'INFO', '    1.13.1-foss-2018b-Python-3.6.6 (-2)'),
            ('application', 'INFO', '    1.13.1-fosscuda-2018b-Python-3.6.6 (-10)'),
        )

    @log_capture()
    def test_get_description(self, log):
        """
        Test the get_description output
        """
        tf = Application.objects.get(name='TensorFlow')
        get_description(application=tf)
        log.check(
            (
                'application',
                'INFO',
                'The description for Application object (3) is\n'
                'An open-source software library for Machine Intelligence',
            ),
        )

    @log_capture()
    def test_rename_application(self, log):
        """
        Test rename_application
        """
        tf = Application.objects.get(name='TensorFlow')
        self.assertEqual(tf.name, "TensorFlow")
        rename_application(application=tf, newname="Penguins")
        log.check(('application', 'INFO', 'Renamed TensorFlow to Penguins'))
        self.assertEqual(tf.name, "Penguins")

    @log_capture()
    def test_change_more_information(self, log):
        """
        Test change_more_information
        """
        tf = Application.objects.get(name='TensorFlow')
        self.assertEqual(tf.more_info, "https://www.tensorflow.org/")
        change_more_information(application=tf, link='https://new.link/')
        log.check(('application', 'INFO', 'More info link for TensorFlow changed to https://new.link/'))
        self.assertEqual(tf.more_info, "https://new.link/")

    @log_capture()
    def test_change_description_no_file(self, log):
        """
        Test change_description with no file
        """
        with self.assertRaises(SystemExit) as cm:
            change_description(application="info", filename="temp.txt")
        self.assertEqual(cm.exception.code, 1)
        log.check(("functions", "ERROR", "Error ([Errno 2] No such file or directory: 'temp.txt') reading temp.txt"))

    @tempdir()
    @log_capture()
    def test_change_description_match(self, log, dir):
        """
        Test change_description
        """
        tf = Application.objects.get(name="TensorFlow")
        txt = "".join(paragraphs(2, common=False))
        dir.write("temp.txt", bytes(txt, encoding="UTF-8"))
        change_description(
            application=tf, filename=os.path.join(dir.path, "temp.txt"),
        )
        self.assertEqual(txt, tf.description)
        log.check(("application", "INFO", "Changed description for TensorFlow"))
