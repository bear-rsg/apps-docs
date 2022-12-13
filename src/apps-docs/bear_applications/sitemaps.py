from django.contrib.sitemaps import Sitemap
from django.db.models import Count, F
from django.urls import reverse
from .models import Application, Link, Version
from .views import SPECIAL_PAGE_NAMES


class IndexSitemap(Sitemap):
    # changefreq is how often the page will change, which for version pages is rarely
    changefreq = "daily"
    # these pages are more important, so push their priority higher
    priority = 0.9

    def items(self):
        return [
            'bear_applications:home',
            'bear_applications:applications',
        ]

    def lastmod(self, obj):
        v = Version.objects.order_by('-modified')[0]
        return v.modified

    def location(self, obj):
        return reverse(obj)


class StaticSitemap(Sitemap):
    changefreq = "monthly"

    def items(self):
        return [
            'bear_applications:search',
            'bear_applications:filter_options',
            'bear_applications:cookies',
            'bear_applications:help',
        ]

    def location(self, obj):
        return reverse(obj)


class VersionSitemap(Sitemap):
    changefreq = "monthly"

    def items(self):
        return Version.objects.annotate(numlink=Count('link')).filter(
            reason_to_hide=None, numlink__gt=0, application__reason_to_hide=None).exclude(
            version__in=SPECIAL_PAGE_NAMES).order_by('application__name', 'version')

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        return reverse('bear_applications:application_version',
                       kwargs={'bavname': obj.link_set.all()[0].bearappsversion.displayed_name,
                               'name': obj.application.name, 'version': obj.version})


class ApplicationSitemap(Sitemap):
    changefreq = "monthly"

    def items(self):
        return (Application.objects.annotate(num_versions=Count('version'))
                                   .filter(reason_to_hide=None, version__reason_to_hide=None, num_versions__gt=0)
                                   .order_by('name'))

    def lastmod(self, obj):
        return Version.objects.filter(application=obj).order_by('-modified')[0].modified

    def location(self, obj):
        return reverse('bear_applications:application', kwargs={'name': obj.name})


class FilterSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return (Link.objects.filter(version__reason_to_hide=None, version__application__reason_to_hide=None,
                                    bearappsversion__hidden=False, architecture__hidden=False)
                            .exclude(bearappsversion__name='system', architecture__name='system')
                            .values(bav=F('bearappsversion__displayed_name'), arch=F('architecture__displayed_name'))
                            .distinct().order_by('bav', 'arch'))

    def location(self, obj):
        return reverse('bear_applications:filter',
                       kwargs={'bearappsversion': obj['bav'], 'arch': obj['arch']})


class ArchitectureSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return (Link.objects.filter(version__reason_to_hide=None, version__application__reason_to_hide=None,
                                    bearappsversion__hidden=False, architecture__hidden=False)
                            .exclude(architecture__name='system')
                            .values(arch=F('architecture__displayed_name')).distinct().order_by('arch'))

    def location(self, obj):
        return reverse('bear_applications:filter', kwargs={'bearappsversion': 'all', 'arch': obj['arch']})


class BEARAppsVersionSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return (Link.objects.filter(version__reason_to_hide=None, version__application__reason_to_hide=None,
                                    bearappsversion__hidden=False, architecture__hidden=False)
                            .exclude(bearappsversion__name='system')
                            .values(bav=F('bearappsversion__displayed_name')).distinct().order_by('bav'))

    def location(self, obj):
        return reverse('bear_applications:filter', kwargs={'bearappsversion': obj['bav']})
