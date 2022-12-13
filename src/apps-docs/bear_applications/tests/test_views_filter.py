from django.test import TestCase
from django.urls import reverse


class FilterTestCase(TestCase):
    """
    Test the filter pages - the ones that filter be bearappsversion and/or architecture
    """
    fixtures = ['db.json']

    def test_nonexistent_bearappsversion(self):
        """
        nonexistent bearappsversion - should 404
        """
        response = self.client.get(reverse('bear_applications:filter', args=['pooiydwssdsddsnask']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_nonexistent_architecture(self):
        """
        nonexistent architecture - should 404
        """
        response = self.client.get(reverse('bear_applications:filter', args=['all', 'pooiydwssdsddsnask']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_hidden_architecture(self):
        """
        hidden architecture - should 404
        """
        response = self.client.get(reverse('bear_applications:filter', args=['all', 'BB-Hidden-Arch']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_nonexistent_bearappsversion_and_architecture(self):
        """
        nonexistent bearappsversion and architecture - should 404
        """
        response = self.client.get(reverse('bear_applications:filter', args=['pooiydwssdsddsnask',
                                                                             'pooiydwssdsddsnask']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_existent_bearappsversion_and_hidden_architecture(self):
        """
        existent bearappsversion and hidden architecture - should 404
        """
        response = self.client.get(reverse('bear_applications:filter', args=['2018b', 'BB-Hidden-Arch']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_existent_bearappsversion(self):
        """
        existent bearappsversion
        """
        response = self.client.get(reverse('bear_applications:filter', args=['2018b']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter.html')
        self.assertEqual(len(response.context['applications']), 5)
        self.assertEqual(response.context['bearappsversion'], '2018b')
        self.assertEqual(response.context['arch'], None)
        self.assertEqual(response.context['deprecated'], False)

    def test_existent_architecture(self):
        """
        existent architecture
        """
        response = self.client.get(reverse('bear_applications:filter', args=['all', 'EL7-haswell']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter.html')
        self.assertEqual(len(response.context['applications']), 6)
        self.assertEqual(response.context['bearappsversion'], 'all')
        self.assertEqual(response.context['arch'], 'EL7-haswell')
        self.assertEqual(response.context['deprecated'], False)

    def test_existent_bearappsversion_and_architecture(self):
        """
        existent bearappsversion and architecture
        """
        response = self.client.get(reverse('bear_applications:filter', args=['2018b', 'EL7-haswell']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter.html')
        self.assertEqual(len(response.context['applications']), 4)
        self.assertEqual(response.context['bearappsversion'], '2018b')
        self.assertEqual(response.context['arch'], 'EL7-haswell')
        self.assertEqual(response.context['deprecated'], False)

    def test_deprecated_bearappsversion(self):
        """
        existent bearappsversion and architecture
        """
        response = self.client.get(reverse('bear_applications:filter', args=['2017a']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter.html')
        self.assertEqual(len(response.context['applications']), 1)
        self.assertEqual(response.context['bearappsversion'], '2017a')
        self.assertEqual(response.context['arch'], None)
        self.assertEqual(response.context['deprecated'], True)

    def test_deprecated_bearappsversion_and_architecture(self):
        """
        existent bearappsversion and architecture
        """
        response = self.client.get(reverse('bear_applications:filter', args=['2017a', 'EL7-haswell']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bear_applications/filter.html')
        self.assertEqual(len(response.context['applications']), 0)
        self.assertEqual(response.context['bearappsversion'], '2017a')
        self.assertEqual(response.context['arch'], 'EL7-haswell')
        self.assertEqual(response.context['deprecated'], True)
