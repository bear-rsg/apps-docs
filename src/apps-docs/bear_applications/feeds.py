from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Version


class LatestApplicationsFeed(Feed):
    title = settings.WEBSITE_SITE_CONFIG['WEBSITE_NAME']
    link = '/latest-applications-feed'
    description = f"Latest applications installed on {settings.WEBSITE_SITE_CONFIG['SYSTEM_NAME']}. " \
                  "Provided by Advanced Research Computing for researchers at the University of Birmingham."

    def items(self):
        return Version.objects.filter(reason_to_hide=None,
                                      application__reason_to_hide=None).order_by('-modified')[:100]

    def item_title(self, item):
        return "{} - {}".format(item.application.name, item.version)

    def item_description(self, item):
        return item.application.description.replace('\n', '')

    def item_link(self, item):
        return reverse('bear_applications:application_version',
                       kwargs={'bavname': item.link_set.all().order_by('-id')[0].bearappsversion.displayed_name,
                               'name': item.application.name, 'version': item.version})
