from collections import ChainMap
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse


class FilterOptionsTestCase(TestCase):
    """
    Test the filter options page
    """
    fixtures = ['db.json']

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': True, 'BAV_ORDER': 'desc'},
                       settings.WEBSITE_SITE_CONFIG))
    def test_filter_options_with_arch(self):
        response = self.client.get(reverse('bear_applications:filter_options'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter_options.html')
        self.assertEqual(len(response.context['bearappversions']), 5)
        self.assertEqual("2019b", response.context['bearappversions'][0]['bav'])
        self.assertEqual("2019a", response.context['bearappversions'][1]['bav'])
        self.assertEqual("2019h", response.context['bearappversions'][2]['bav'])
        self.assertEqual("2018b", response.context['bearappversions'][3]['bav'])
        self.assertEqual("2017a", response.context['bearappversions'][4]['bav'])
        self.assertEqual(len(response.context['architectures']), 2)
        self.assertEqual(len(response.context['combos']), 5)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': False, 'BAV_ORDER': 'desc'},
                       settings.WEBSITE_SITE_CONFIG))
    def test_filter_options_no_arch(self):
        response = self.client.get(reverse('bear_applications:filter_options'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter_options.html')
        self.assertEqual(len(response.context['bearappversions']), 5)
        self.assertEqual("2019b", response.context['bearappversions'][0]['bav'])
        self.assertEqual("2019a", response.context['bearappversions'][1]['bav'])
        self.assertEqual("2019h", response.context['bearappversions'][2]['bav'])
        self.assertEqual("2018b", response.context['bearappversions'][3]['bav'])
        self.assertEqual("2017a", response.context['bearappversions'][4]['bav'])
        self.assertEqual(len(response.context['architectures']), 0)
        self.assertEqual(len(response.context['combos']), 0)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': True, 'BAV_ORDER': 'asc'},
                       settings.WEBSITE_SITE_CONFIG))
    def test_filter_options_av_order(self):
        response = self.client.get(reverse('bear_applications:filter_options'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter_options.html')
        self.assertEqual(len(response.context['bearappversions']), 5)
        self.assertEqual("2017a", response.context['bearappversions'][0]['bav'])
        self.assertEqual("2018b", response.context['bearappversions'][1]['bav'])
        self.assertEqual("2019a", response.context['bearappversions'][2]['bav'])
        self.assertEqual("2019b", response.context['bearappversions'][3]['bav'])
        self.assertEqual("2019h", response.context['bearappversions'][4]['bav'])
        self.assertEqual(len(response.context['architectures']), 2)
        self.assertEqual(len(response.context['combos']), 5)
