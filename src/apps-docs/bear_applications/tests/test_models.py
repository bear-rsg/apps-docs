from django.apps import apps
from django.test import TestCase
from bear_applications.models import Version
from bear_applications.apps import BearApplicationsConfig


class BearApplicationsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(BearApplicationsConfig.name, 'bear_applications')
        self.assertEqual(apps.get_app_config('bear_applications').name, 'bear_applications')


class VersionModelTestCase(TestCase):
    """
    Test the Version model
    """
    fixtures = ['db.json']

    def test_version_dependencies(self):
        """
        Test the sorted_dependencies for a version
        """
        tf = Version.objects.get(application__name='TensorFlow', version='1.13.1-foss-2018b-Python-3.6.6')
        self.assertEqual(tf.dependencies.count(), 2)
        self.assertEqual(tf.sorted_dependencies[0].application.name, 'PyTorch')
        self.assertEqual(tf.sorted_dependencies[0].version, '1.2.0-fosscuda-2019a-Python-3.7.2')
        self.assertEqual(tf.sorted_dependencies[1].application.name, 'TensorFlow')
        self.assertEqual(tf.sorted_dependencies[1].version, '1.13.1-fosscuda-2018b-Python-3.6.6')

    def test_version_requires(self):
        """
        Test the sorted_requires for a version
        """
        tf = Version.objects.get(application__name='TensorFlow', version='1.13.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(tf.requires.count(), 2)
        self.assertEqual(tf.sorted_requires[0].application.name, 'Python')
        self.assertEqual(tf.sorted_requires[0].version, '2.7.12-foss-2012a')
        self.assertEqual(tf.sorted_requires[1].application.name, 'TensorFlow')
        self.assertEqual(tf.sorted_requires[1].version, '1.13.1-foss-2018b-Python-3.6.6')
