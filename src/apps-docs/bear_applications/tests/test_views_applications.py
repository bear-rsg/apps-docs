from django.test import TestCase
from django.urls import reverse


class ApplicationsTestCase(TestCase):
    """
    Test the applications page - the one that lists all current applications
    """
    fixtures = ['db.json']

    def test_applications(self):
        """
        applications page
        """
        response = self.client.get(reverse('bear_applications:applications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/applications.html')
        self.assertEqual(len(response.context['applications']), 1)
