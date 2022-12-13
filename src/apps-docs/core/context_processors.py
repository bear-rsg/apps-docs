from django.conf import settings


def base_template(request):
    return {'BASE_TEMPLATE': settings.WEBSITE_SITE_CONFIG['BASE_TEMPLATE']}
