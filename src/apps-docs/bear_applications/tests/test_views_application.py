from django.test import TestCase
from django.urls import reverse


class ApplicationTestCase(TestCase):
    """
    Test the application page - the one that shows all versions of an application
    """
    fixtures = ['db.json']

    def test_nonexistent_app(self):
        """
        nonexistent app - should 404
        """
        response = self.client.get(reverse('bear_applications:application', args=['pooiydwssdsddsnask']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_existent_app_with_paragraphdata(self):
        """
        existent app, with paragraph data
        """
        response = self.client.get(reverse('bear_applications:application', args=['MATLAB']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/application.html')
        self.assertEqual(response.context['application'].name, 'MATLAB')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 2)
        self.assertEqual(response.context['application'].paragraphdata_set.all()[0].header, 'first paragraph')
        self.assertEqual(response.context['application'].paragraphdata_set.all()[1].header, 'second paragraph')
        self.assertEqual(len(response.context['versions']), 3)
        self.assertEqual(response.context['versions'][0]['version'], '2017a')
        self.assertEqual(response.context['versions'][1]['version'], '2017b')
        self.assertEqual(response.context['versions'][2]['version'], 'R2018b')

    def test_existent_app_with_no_paragraphdata(self):
        """
        existent app, with no paragraph data
        """
        response = self.client.get(reverse('bear_applications:application', args=['TensorFlow']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/application.html')
        self.assertEqual(response.context['application'].name, 'TensorFlow')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 0)
        self.assertEqual(len(response.context['versions']), 7)
        self.assertEqual(response.context['versions'][0]['version'], '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(response.context['versions'][1]['version'], '1.10.1-foss-2017a-Python-3.6.6')
        self.assertEqual(response.context['versions'][2]['version'], '1.10.1-fosscuda-2018b-Python-3.6.6')
        self.assertEqual(response.context['versions'][3]['version'], '1.10.1-foss-2018b-Python-3.6.6')
        self.assertEqual(response.context['versions'][4]['version'], '1.13.1-foss-2018b-Python-3.6.6')

    def test_archived_app(self):
        """
        archived app
        """
        response = self.client.get(reverse('bear_applications:application', args=['Python']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_all_versions_archived(self):
        """
        all versions of app archived
        """
        response = self.client.get(reverse('bear_applications:application', args=['PyTorch']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_app_with_information_page_version(self):
        """
        version of app is named 'Information Page'
        """
        response = self.client.get(reverse('bear_applications:application', args=['Singularity']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/application.html')
        self.assertEqual(response.context['application'].name, 'Singularity')
        self.assertEqual(len(response.context['application'].paragraphdata_set.all()), 1)
        self.assertEqual(response.context['versions'], None)
