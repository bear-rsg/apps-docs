from django.test import TestCase
from django.urls import reverse


class FeedTestCase(TestCase):
    """
    Test the latest applications feed
    """
    fixtures = ['db.json']

    def test_feed(self):
        """
        feed
        """
        response = self.client.get(reverse('bear_applications:latest-applications-feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('bear_applications:application_version',
                                              kwargs={'bavname': '2018b', 'name': 'MATLAB', 'version': 'R2018b'}))


class SitemapTestCase(TestCase):
    """
    Test the sitemap
    """
    fixtures = ['db.json']

    def test_sitemap(self):
        """
        sitemap
        """
        response = self.client.get(reverse('bear_applications:sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('bear_applications:home'))
        self.assertContains(response, reverse('bear_applications:applications'))
        self.assertContains(response, reverse('bear_applications:search'))
        self.assertContains(response, reverse('bear_applications:filter_options'))
        self.assertContains(response, reverse('bear_applications:cookies'))
        self.assertContains(response, reverse('bear_applications:help'))
        self.assertContains(response, reverse('bear_applications:application_version',
                                              kwargs={'bavname': '2018b', 'name': 'MATLAB', 'version': 'R2018b'}))
        self.assertContains(response, reverse('bear_applications:application', kwargs={'name': 'MATLAB'}))
        self.assertContains(response, reverse('bear_applications:filter',
                                              kwargs={'bearappsversion': '2019a', 'arch': 'EL7-haswell'}))
        self.assertContains(response, reverse('bear_applications:filter',
                                              kwargs={'bearappsversion': 'all', 'arch': 'EL7-haswell'}))
        self.assertContains(response, reverse('bear_applications:filter', kwargs={'bearappsversion': '2018b'}))
