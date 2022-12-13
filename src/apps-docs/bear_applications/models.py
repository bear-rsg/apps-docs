from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class Application(models.Model):
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    more_info = models.TextField(blank=True)
    reason_to_hide = models.TextField(null=True)


class Version(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    version = models.CharField(max_length=255)
    module_load = models.TextField(blank=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    reason_to_hide = models.TextField(null=True)
    dependencies = models.ManyToManyField('self', symmetrical=False, related_name='requires')
    app_sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = (('application', 'version'),)
        ordering = ['-app_sort_order', '-version', ]

    @property
    def sorted_dependencies(self):
        return self.dependencies.all().order_by(Lower('application__name'))

    @property
    def sorted_requires(self):
        return self.requires.all().order_by(Lower('application__name'))


class CurrentVersion(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)


class ParagraphData(models.Model):
    version = models.ForeignKey(Version, blank=True, null=True, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, blank=True, null=True, on_delete=models.CASCADE)
    header = models.CharField(max_length=255)
    content = models.TextField()
    added_by = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('version', 'header'),)
        ordering = ['created', ]


class Architecture(models.Model):
    name = models.CharField(unique=True, max_length=255)
    displayed_name = models.TextField()
    hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ['name', ]


class BearAppsVersion(models.Model):
    name = models.CharField(unique=True, max_length=255)
    displayed_name = models.TextField()
    auto_loaded = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    supported = models.BooleanField(default=True)

    class Meta:
        if settings.WEBSITE_SITE_CONFIG['BAV_ORDER'] == 'asc':
            ordering = ['displayed_name', ]
        else:
            ordering = ['-displayed_name', ]


class Link(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    bearappsversion = models.ForeignKey(BearAppsVersion, on_delete=models.CASCADE)
    architecture = models.ForeignKey(Architecture, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('version', 'bearappsversion', 'architecture'),)
        ordering = ['-bearappsversion__displayed_name', 'architecture__name', ]


class Gpu(models.Model):
    name = models.CharField(max_length=255)
    architecture = models.ForeignKey(Architecture, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('name', 'architecture'),)
        ordering = ['name']
