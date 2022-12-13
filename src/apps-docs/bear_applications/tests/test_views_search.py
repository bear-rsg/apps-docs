from django.test import TestCase
from django.urls import reverse


class SearchTestCase(TestCase):
    """
    Test the search page
    """
    fixtures = ['db.json']

    def test_search_no_search_string(self):
        """
        search page, no search string
        """
        response = self.client.get(reverse('bear_applications:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'], {'and_or': 'and', 'partial_exact': 'partial'})

    def test_search_empty_search_string(self):
        """
        search page, empty single search string
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'], {'and_or': 'and', 'partial_exact': 'partial'})

    def test_search_simple_search_string(self):
        """
        search page, sensible single search string
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': 'matlab'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 4)
        self.assertEqual(response.context['searched'], {'name': 'matlab', 'and_or': 'and', 'partial_exact': 'partial'})

    def test_search_simple_search_string_with_padding(self):
        """
        search page, sensible single search string with whitespace
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': ' matlab '})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 4)
        self.assertEqual(response.context['searched'], {'name': 'matlab', 'and_or': 'and', 'partial_exact': 'partial'})
        self.assertEqual(response.context['appversions'][0]['ver'], '2017a')
        self.assertEqual(response.context['appversions'][1]['ver'], '2017b')
        self.assertEqual(response.context['appversions'][2]['ver'], 'R2018b')

    def test_search_simple_search_string_archived_app(self):
        """
        search page, sensible single search string of archived app
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': 'python'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        # this matches the TensorFlow versions , as they have python in the name
        self.assertEqual(len(response.context['appversions']), 5)
        self.assertEqual(response.context['searched'],
                         {'name': 'python', 'and_or': 'and', 'partial_exact': 'partial'})

    def test_search_simple_search_string_archived_version(self):
        """
        search page, sensible single search string of archived version
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': 'pytorch'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'],
                         {'name': 'pytorch', 'and_or': 'and', 'partial_exact': 'partial'})

    def test_search_simple_nonsense_search_string(self):
        """
        search page, nonesense single search string
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': 'pooiydwssdsddsnask'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'],
                         {'name': 'pooiydwssdsddsnask', 'and_or': 'and', 'partial_exact': 'partial'})

    def test_search_complex_empty_name_search_string(self):
        """
        search page, sensible complex search on name
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': '', 'version': '', 'module': '', 'other': '', 'and_or': 'and',
                                    'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'],
                         {'and_or': 'and', 'partial_exact': 'partial', 'deprecated': 'no'})

    def test_search_complex_name_search_string(self):
        """
        search page, sensible complex search on name
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'matlab', 'version': '', 'module': '', 'other': '', 'and_or': 'and',
                                    'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 4)
        self.assertEqual(response.context['searched'],
                         {'name': 'matlab', 'and_or': 'and', 'partial_exact': 'partial', 'deprecated': 'no'})

    def test_search_complex_search_archived_app(self):
        """
        search page, sensible complex search of archived app
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'python', 'version': '', 'module': '', 'other': '', 'and_or': 'and',
                                    'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'],
                         {'name': 'python', 'and_or': 'and', 'partial_exact': 'partial', 'deprecated': 'no'})

    def test_search_complex_search_archived_version(self):
        """
        search page, sensible complex search of archived version
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': 'pytorch'},
                                   {'name': 'pytorch', 'version': '1.2.0-fosscuda-2019a-Python-3.7.2', 'module': '',
                                    'other': '', 'and_or': 'and', 'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'],
                         {'name': 'pytorch', 'and_or': 'and', 'partial_exact': 'partial'})

    def test_search_complex_name_and_version_search_string(self):
        """
        search page, sensible complex search on name and version
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'matlab', 'version': '2017', 'module': '', 'other': '', 'and_or': 'and',
                                    'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 2)
        self.assertEqual(response.context['searched'],
                         {'name': 'matlab', 'version': '2017', 'and_or': 'and', 'partial_exact': 'partial',
                          'deprecated': 'no'})

    def test_search_complex_name_or_version_search_string(self):
        """
        search page, sensible complex search on name or version
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'tensorflow', '2018': '', 'module': '', 'other': '', 'and_or': 'or',
                                    'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 3)
        self.assertEqual(response.context['searched'],
                         {'name': 'tensorflow', 'partial_exact': 'partial', 'deprecated': 'no'})

    def test_search_complex_name_or_version_search_string_deprecated(self):
        """
        search page, sensible complex search on name or version and include deprecated BEAR Apps Versions
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'tensorflow', '2018': '', 'module': '', 'other': '', 'and_or': 'or',
                                    'partial_exact': 'partial', 'deprecated': 'yes'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 5)
        self.assertEqual(response.context['searched'], {'name': 'tensorflow', 'partial_exact': 'partial'})

    def test_search_complex_name_search_exact_string(self):
        """
        search page, sensible complex exact search on name
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'matlab', 'version': '', 'module': '', 'other': '', 'and_or': 'and',
                                    'partial_exact': 'exact'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 3)
        self.assertEqual(response.context['searched'], {'name': 'matlab', 'and_or': 'and'})

    def test_search_complex_name_and_version_search_exact_string(self):
        """
        search page, sensible complex exact search on name and version
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'matlab', 'version': '2017', 'module': '', 'other': '', 'and_or': 'and',
                                    'partial_exact': 'exact', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'],
                         {'name': 'matlab', 'version': '2017', 'and_or': 'and', 'deprecated': 'no'})

    def test_search_complex_name_or_version_search_exact_string(self):
        """
        search page, sensible complex exact search on name or version
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': 'tensorflow', '2018': '', 'module': '', 'other': '', 'and_or': 'or',
                                    'partial_exact': 'exact', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 3)
        self.assertEqual(response.context['searched'], {'name': 'tensorflow', 'deprecated': 'no'})

    def test_search_complex_module_search_exact_string(self):
        """
        search page, sensible complex exact search on module
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': '', 'version': '', 'module': 'apps/matlab/2017b', 'other': '',
                                    'and_or': 'or', 'partial_exact': 'exact', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 1)
        self.assertEqual(response.context['searched'], {'module': 'apps/matlab/2017b', 'deprecated': 'no'})

    def test_search_complex_module_search_partial_string(self):
        """
        search page, sensible complex partial search on module
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': '', 'version': '', 'module': 'apps', 'other': '',
                                    'and_or': 'or', 'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 2)
        self.assertEqual(response.context['searched'],
                         {'module': 'apps', 'partial_exact': 'partial', 'deprecated': 'no'})

    def test_search_complex_other_search_exact_string(self):
        """
        search page, sensible complex exact search on other
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': '', 'version': '', 'module': '', 'other': 'mat',
                                    'and_or': 'or', 'partial_exact': 'exact', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 0)
        self.assertEqual(response.context['searched'], {'other': 'mat', 'deprecated': 'no'})

    def test_search_complex_other_search_partial_string(self):
        """
        search page, sensible complex partial search on other
        """
        response = self.client.get(reverse('bear_applications:search'),
                                   {'name': '', 'version': '', 'module': '', 'other': 't',
                                    'and_or': 'or', 'partial_exact': 'partial', 'deprecated': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 8)
        self.assertEqual(response.context['searched'], {'other': 't', 'partial_exact': 'partial', 'deprecated': 'no'})

    def test_search_on_paragraphdata_header(self):
        """
        search page, text that is only in the header of paragraph data
        """
        response = self.client.get(reverse('bear_applications:search'), {'search': 'unusual'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/search.html')
        self.assertEqual(len(response.context['appversions']), 1)
        self.assertEqual(response.context['searched'],
                         {'name': 'unusual', 'and_or': 'and', 'partial_exact': 'partial'})
