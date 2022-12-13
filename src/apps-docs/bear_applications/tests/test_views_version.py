from collections import ChainMap
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse


class VersionTestCase(TestCase):
    """
    Test the version page - the one that shows a version of an application
    """
    fixtures = ['db.json']

    def test_nonexistent_app(self):
        """
        nonexistent application - should 404
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'pooiydwssdsddsnask', 'pooiydwssdsddsnask']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_nonexistent_version(self):
        """
        nonexistent version - should 404
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'MATLAB', 'pooiydwssdsddsnask']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_current_version_with_needs_module(self):
        """
        current version
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2018b', 'MATLAB', 'R2018b']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'MATLAB')
        self.assertEqual(response.context['application'].version, 'R2018b')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 2)
        self.assertEqual(response.context['application'].paragraphdata_set.all()[0].header, 'a title')
        self.assertEqual(response.context['application'].paragraphdata_set.all()[1].header, 'some title')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 2)
        self.assertEqual(response.context['application'].application.paragraphdata_set.all()[0].header,
                         'first paragraph')
        self.assertEqual(response.context['application'].application.paragraphdata_set.all()[1].header,
                         'second paragraph')
        self.assertEqual(len(response.context['archs']), 0)
        self.assertEqual(len(response.context['other_versions']), 2)
        self.assertEqual(response.context['needs_module'], f"{settings.WEBSITE_SITE_CONFIG['MODULE_BASE']}/2018b")
        self.assertEqual(response.context['deprecated'], False)
        self.assertEqual(response.context['sibling_version'], None)
        self.assertEqual(response.context['sibling_version_is'], None)
        self.assertNotContains(response, 'There is a newer version of')
        self.assertNotContains(response, 'There is a CPU version of this module')
        self.assertNotContains(response, 'There is a GPU enabled version of this module')
        self.assertNotContains(response, 'is deprecated')
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    def test_current_version_without_needs_module(self):
        """
        current version
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2019h', 'TensorFlow', '1.13.1-fosscuda-2018b-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.13.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 0)
        self.assertEqual(len(response.context['other_versions']), 5)
        self.assertEqual(response.context['needs_module'], '')
        self.assertEqual(response.context['deprecated'], True)
        self.assertEqual(response.context['sibling_version'].version, '1.13.1-foss-2018b-Python-3.6.6')
        self.assertEqual(response.context['sibling_version_is'], 'CPU')
        self.assertNotContains(response, 'There is a newer version of')
        self.assertContains(response, 'There is a CPU version of this module')
        self.assertContains(response, 'There is a CPU version of this module')
        self.assertNotContains(response, 'There is a GPU enabled version of this module')
        self.assertContains(response, 'is deprecated')
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 2)
        self.assertEqual(response.context['other_versions'][0]['version'], '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(response.context['other_versions'][1]['version'], '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(response.context['other_versions'][2]['version'], '1.10.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(response.context['other_versions'][3]['version'], '1.10.1-foss-2018b-Python-3.6.6')
        self.assertEqual(response.context['other_versions'][4]['version'], '1.13.1-foss-2018b-Python-3.6.6')
        self.assertEqual(len(response.context['multideps']), 0)

    def test_non_current_version_without_needs_module(self):
        """
        current version
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'TensorFlow', '1.13.1-foss-2018b-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.13.1-foss-2018b-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 0)
        self.assertEqual(len(response.context['other_versions']), 6)
        self.assertEqual(response.context['needs_module'],
                         f"{settings.WEBSITE_SITE_CONFIG['MODULE_BASE']}-unsupported/2017a")
        self.assertEqual(response.context['deprecated'], True)
        self.assertEqual(response.context['sibling_version'].version, '1.13.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(response.context['sibling_version_is'], 'GPU enabled')
        self.assertNotContains(response, 'There is a newer version of')
        self.assertNotContains(response, 'There is a CPU version of this module')
        self.assertContains(response, 'There is a GPU enabled version of this module')
        self.assertNotContains(response, 'is deprecated')
        self.assertEqual(len(response.context['application'].dependencies.all()), 2)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    def test_old_version_with_needs_module(self):
        """
        current version
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2018b', 'MATLAB', '2017a']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'MATLAB')
        self.assertEqual(response.context['application'].version, '2017a')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 2)
        self.assertEqual(response.context['application'].application.paragraphdata_set.all()[0].header,
                         'first paragraph')
        self.assertEqual(response.context['application'].application.paragraphdata_set.all()[1].header,
                         'second paragraph')
        self.assertEqual(len(response.context['archs']), 0)
        self.assertEqual(len(response.context['other_versions']), 2)
        self.assertEqual(response.context['needs_module'], f"{settings.WEBSITE_SITE_CONFIG['MODULE_BASE']}/2018b")
        self.assertEqual(response.context['deprecated'], False)
        self.assertEqual(response.context['sibling_version'], None)
        self.assertEqual(response.context['sibling_version_is'], None)
        self.assertContains(response, 'There is a newer version of')
        self.assertNotContains(response, 'There is a CPU version of this module')
        self.assertNotContains(response, 'There is a GPU enabled version of this module')
        self.assertNotContains(response, 'is deprecated')
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 1)
        self.assertEqual(len(response.context['multideps']), 0)

    def test_multideps(self):
        """
        test a module that has multideps
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                   args=['2019a', 'matlab_toolbox', '1.0']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(len(response.context['application'].dependencies.all()), 2)
        self.assertEqual(response.context['multideps'][0], 'MATLAB')
        self.assertContains(response, 'multiple vesions of')

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': True}, settings.WEBSITE_SITE_CONFIG))
    def test_deprecated_and_unsupported_with_arch(self):
        """
        deprecated version
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'TensorFlow', '1.10.1-foss-2017a-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 1)
        self.assertEqual(len(response.context['other_versions']), 5)
        self.assertEqual(response.context['needs_module'],
                         f"{settings.WEBSITE_SITE_CONFIG['MODULE_BASE']}-unsupported/2017a")
        self.assertEqual(response.context['deprecated'], True)
        self.assertEqual(response.context['sibling_version'], None)
        self.assertEqual(response.context['sibling_version_is'], None)
        self.assertContains(response, 'There is a newer version of')
        self.assertNotContains(response, 'There is a CPU version of this module')
        self.assertNotContains(response, 'There is a GPU enabled version of this module')
        self.assertContains(response, 'is not supported')
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': False}, settings.WEBSITE_SITE_CONFIG))
    def test_deprecated_and_unsupported_no_arch(self):
        """
        unsupported version
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'TensorFlow', '1.10.1-foss-2017a-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 0)
        self.assertEqual(len(response.context['other_versions']), 5)
        self.assertEqual(response.context['needs_module'],
                         f"{settings.WEBSITE_SITE_CONFIG['MODULE_BASE']}-unsupported/2017a")
        self.assertEqual(response.context['deprecated'], True)
        self.assertEqual(response.context['sibling_version'], None)
        self.assertEqual(response.context['sibling_version_is'], None)
        self.assertContains(response, 'There is a newer version of')
        self.assertNotContains(response, 'There is a CPU version of this module')
        self.assertNotContains(response, 'There is a GPU enabled version of this module')
        self.assertContains(response, 'is not supported')
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    def test_archived_version(self):
        """
        archived version
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2018b', 'PyTorch', '1.2.0-fosscuda-2019a-Python-3.7.2']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_version_of_archived_app(self):
        """
        version of archived app
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2019a', 'Python', '2.7.12-foss-2012a']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_version_called_information_page(self):
        """
        version is named 'Information Page'
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['system', 'Singularity', 'Information Page']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'Singularity')
        self.assertEqual(response.context['application'].version, 'Information Page')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['other_versions']), 0)
        self.assertEqual(len(response.context['archs']), 0)
        self.assertEqual(response.context['sibling_version'], None)
        self.assertEqual(response.context['sibling_version_is'], None)
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': True}, settings.WEBSITE_SITE_CONFIG))
    def test_architecture_hidden_on_version_page_with_arch(self):
        """
        Ensure that a hidden architecture is not shown as supported
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'TensorFlow', '1.10.1-foss-2017a-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 1)
        self.assertEqual(len(response.context['other_versions']), 5)
        self.assertNotContains(response, 'BB-Hidden-Arch')
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': True}, settings.WEBSITE_SITE_CONFIG))
    def test_architecture_shown_on_version_page_with_arch(self):
        """
        Ensure that a non-hidden architecture is shown as supported
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'TensorFlow', '1.10.1-foss-2017a-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 1)
        self.assertContains(response, 'EL7-power9')
        self.assertEqual(len(response.context['other_versions']), 5)
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': False}, settings.WEBSITE_SITE_CONFIG))
    def test_architecture_hidden_on_version_page_no_arch(self):
        """
        Ensure that a hidden architecture is not shown as supported
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'TensorFlow', '1.10.1-foss-2017a-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 0)
        self.assertEqual(len(response.context['other_versions']), 5)
        self.assertNotContains(response, 'BB-Hidden-Arch')
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': False}, settings.WEBSITE_SITE_CONFIG))
    def test_architecture_shown_on_version_page_no_arch(self):
        """
        Ensure that a non-hidden architecture is shown as supported
        """
        response = self.client.get(reverse('bear_applications:application_version',
                                           args=['2017a', 'TensorFlow', '1.10.1-foss-2017a-Python-3.6.6']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/version.html')
        self.assertEqual(response.context['application'].application.name, 'TensorFlow')
        self.assertEqual(response.context['application'].version, '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['application'].application.paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['archs']), 0)
        self.assertNotContains(response, 'EL7-power9')
        self.assertEqual(len(response.context['other_versions']), 5)
        self.assertEqual(len(response.context['application'].dependencies.all()), 0)
        self.assertEqual(len(response.context['application'].requires.all()), 0)
        self.assertEqual(len(response.context['multideps']), 0)
