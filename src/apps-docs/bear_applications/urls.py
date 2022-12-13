from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView
from . import views

from django.contrib.sitemaps.views import sitemap
from .sitemaps import (ApplicationSitemap, ArchitectureSitemap, BEARAppsVersionSitemap,
                       FilterSitemap, IndexSitemap, StaticSitemap, VersionSitemap)
from .feeds import LatestApplicationsFeed

sitemaps = {
    'index': IndexSitemap,
    'pages': StaticSitemap,
    'filters': FilterSitemap,
    'architectures': ArchitectureSitemap,
    'bearappsversions': BEARAppsVersionSitemap,
    'versions': VersionSitemap,
    'applications': ApplicationSitemap,
}


app_name = 'bear_applications'
urlpatterns = [
    path('', views.home, name='home'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('index', views.home, name='home'),
    path('search', views.search, name='search'),
    path('filter', views.filter_options, name='filter_options'),
    path('filter/<str:bearappsversion>', views.filter, name='filter'),
    path('filter/<str:bearappsversion>/', views.filter, name='filter'),
    path('filter/<str:bearappsversion>/<str:arch>', views.filter, name='filter'),
    path('filter/<str:bearappsversion>/<str:arch>/', views.filter, name='filter'),
    path('applications/', views.applications, name='applications'),
    path('applications/<str:name>', views.application, name='application'),
    path('applications/<str:name>/', views.application, name='application'),
    path('applications/<str:name>/<str:version>', views.old_application_version, name='old_application_version'),
    path('applications/<str:name>/<str:version>/', views.old_application_version, name='old_application_version'),
    path('applications/<str:bavname>/<str:name>/<str:version>', views.application_version, name='application_version'),
    path('applications/<str:bavname>/<str:name>/<str:version>/', views.application_version, name='application_version'),
    path('cookies', TemplateView.as_view(template_name="bear_applications/cookies.html"), name='cookies'),
    path('accessibility', TemplateView.as_view(template_name="bear_applications/accessibility.html"),
         name='accessibility'),
    path('help', TemplateView.as_view(template_name=f"bear_applications/{settings.WEBSITE_SITE_CONFIG['HELP_PAGE']}"),
         name='help'),
    path('latest-applications-feed', LatestApplicationsFeed(), name='latest-applications-feed'),
]
