from collections import ChainMap
from django.conf import settings
from django.test import TestCase, override_settings
from django.template import Context, Template


class DotWbrTagTest(TestCase):
    """
    Test the dot_wbr template tag
    """
    TEMPLATE = Template("""{% load app_filters %}{{ value | dot_wbr }}""")

    def test_no_wbr_needed(self):
        """
        there should be no <wbr> added here
        """
        rendered = self.TEMPLATE.render(Context({'value': 'MATLAB'}))
        self.assertEqual('MATLAB', rendered)

    def test_wbr_needed(self):
        """
        there should be <wbr> added here
        """
        rendered = self.TEMPLATE.render(Context({'value': 'BSgenome.Mmusculus.UCSC.mm10.masked'}))
        self.assertEqual('BSgenome.<wbr>Mmusculus.<wbr>UCSC.<wbr>mm10.<wbr>masked', rendered)


class ToANameTagTest(TestCase):
    """
    Test the to_a_name template tag
    """
    TEMPLATE = Template("""{% load app_filters %}{{ value | to_a_name }}""")

    def test_no_change_needed(self):
        """
        there should be no change here
        """
        rendered = self.TEMPLATE.render(Context({'value': 'cowplot'}))
        self.assertEqual('cowplot', rendered)

    def test_change_to_lowercase(self):
        """
        there should just be a change to lowercase
        """
        rendered = self.TEMPLATE.render(Context({'value': 'MATLAB'}))
        self.assertEqual('matlab', rendered)

    def test_removing_unwanted_characters(self):
        """
        there should be characters removed here
        """
        rendered = self.TEMPLATE.render(Context({'value': 'BSgenome.Mmusculus.UCSC.mm10.masked'}))
        self.assertEqual('bsgenomemmusculusucscmm10masked', rendered)


class WebsiteSettingsTest(TestCase):
    """
    Test the website settings values
    """
    TEMPLATE = Template("""{% load app_filters %}{% website_settings_value value %}""")

    def test_undefined(self):
        rendered = self.TEMPLATE.render(Context({'value': 'DOES_NOT_EXIST'}))
        self.assertEqual('UNDEFINED', rendered)

    @override_settings(WEBSITE_SITE_CONFIG=ChainMap({'DISPLAY_ARCH': True}, settings.WEBSITE_SITE_CONFIG))
    def test_defined(self):
        rendered = self.TEMPLATE.render(Context({'value': 'DISPLAY_ARCH'}))
        self.assertEqual('True', rendered)
