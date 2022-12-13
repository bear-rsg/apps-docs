from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class HomeTestCase(TestCase):
    """
    Test the home page
    """
    fixtures = ['db.json']

    def test_home(self):
        """
        home page
        """
        response = self.client.get(reverse('bear_applications:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f"bear_applications/{settings.WEBSITE_SITE_CONFIG['HOME_PAGE']}")
        self.assertEqual(len(response.context['recent']), 10)


class CookiesTestCase(TestCase):
    """
    Test the cookies page
    """
    def test_cookies(self):
        """
        cookies page
        """
        response = self.client.get(reverse('bear_applications:cookies'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/cookies.html')


class HelpTestCase(TestCase):
    """
    Test the help page
    """
    def test_help(self):
        """
        help page
        """
        response = self.client.get(reverse('bear_applications:help'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f"bear_applications/{settings.WEBSITE_SITE_CONFIG['HELP_PAGE']}")
