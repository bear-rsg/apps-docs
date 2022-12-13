from django.conf import settings
from django.shortcuts import get_object_or_404, Http404, redirect, render
from django.db.models.functions import Lower, Substr
from django.db.models import Case, Count, F, IntegerField, Q, Value, When
from functools import reduce
from packaging.version import parse as parse_version
import operator

from .models import Application, Version, Link, CurrentVersion, Architecture, BearAppsVersion

TOOLCHAIN_SIBLING_REPLACEMENTS = {
    '-foss-': '-fosscuda-',
    '-fosscuda-': '-foss-',
    '-gompi-': '-gompic-',
    '-gompic-': '-gompi-',
    '-iomkl-': '-iomklc-',
    '-iomklc-': '-iomkl-',
    '-iompi-': '-iompic-',
    '-iompic-': '-iompi-',
    '2021a': '2021a-CUDA-11.3.1',  # must be before the reverse
    '2021a-CUDA-11.3.1': '2021a',
}
GPU_TOOLCHAINS = ['-fosscuda-', '-gompic-', '-iomklc-', '-iompic-']
SPECIAL_PAGE_NAMES = ['Information Page']


def applications(request):
    """
    List of all applications page
    """
    exclude_versions = Link.objects.filter(
        Q(bearappsversion__deprecated=True) | Q(bearappsversion__supported=False)).values_list('version', flat=True)
    applications = (CurrentVersion.objects.filter(version__reason_to_hide=None,
                                                  version__application__reason_to_hide=None)
                                          .exclude(version__id__in=exclude_versions)
                                          .values(name=F('application__name'), ver=F('version__version'),
                                                  bav=F('version__link__bearappsversion__displayed_name'))
                                          .distinct()
                                          .order_by(Lower('name')))
    return render(request, 'bear_applications/applications.html', {'applications': applications})


def old_application_version(request, name, version):
    """
    Capture the old style requests for version of an application pages and attempt to send somewhere sensible
    """
    application = get_object_or_404(Version, application__name=name, version=version, reason_to_hide=None,
                                    application__reason_to_hide=None)
    return redirect('bear_applications:application_version',
                    bavname=application.link_set.all()[0].bearappsversion.name, name=name, version=version)


def application_version(request, bavname, name, version):
    """
    Individual version of an individual application
    """
    application = get_object_or_404(Version, application__name=name, version=version, reason_to_hide=None,
                                    application__reason_to_hide=None)
    archs = (Link.objects.filter(version=application, bearappsversion__hidden=False, architecture__hidden=False,
             bearappsversion__name=bavname).exclude(bearappsversion__name='system', architecture__name='system'))
    other_versions = (Version.objects.filter(application=application.application, reason_to_hide=None)
                                     .exclude(version=version)
                                     .values('version', 'app_sort_order',
                                             bav=F('link__bearappsversion__displayed_name'))
                                     .distinct())
    if other_versions:
        other_versions = sorted(other_versions, key=lambda k: (k['app_sort_order'], parse_version(k['version'])),
                                reverse=True)

    needs_module = ""
    bav = BearAppsVersion.objects.get(displayed_name=bavname)
    if not bav.supported:
        if bavname.endswith('h'):
            needs_module = "{}-unsupported/handbuilt/{}".format(settings.WEBSITE_SITE_CONFIG['MODULE_BASE'],
                                                                bavname[:-1])
        else:
            needs_module = f"{settings.WEBSITE_SITE_CONFIG['MODULE_BASE']}-unsupported/{bavname}"
    elif not bav.auto_loaded:
        needs_module = f"{settings.WEBSITE_SITE_CONFIG['MODULE_BASE']}/{bavname}"

    deprecated = bav.deprecated
    unsupported = not bav.supported

    if not settings.WEBSITE_SITE_CONFIG['DISPLAY_ARCH']:
        archs = []

    cuda = False
    sibling_module_load = None
    for find, replace in TOOLCHAIN_SIBLING_REPLACEMENTS.items():
        if find in application.module_load:
            sibling_module_load = application.module_load.replace(find, replace)
            if replace in GPU_TOOLCHAINS or '-CUDA-' in replace:
                sibling_version_is = 'GPU enabled'
            else:
                sibling_version_is = 'CPU'
            if find in GPU_TOOLCHAINS or '-CUDA-' in find:
                cuda = True

    if not cuda and 'cuda' in application.application.name.lower():
        cuda = True

    try:
        sibling_version = Version.objects.get(application=application.application, module_load=sibling_module_load,
                                              reason_to_hide=None)
    except Version.DoesNotExist:
        sibling_version = None
        sibling_version_is = None

    multideps = (application.sorted_dependencies.values('application')
                                                .annotate(Count('application'))
                                                .filter(application__count__gt=1)
                                                .values_list('application__name', flat=True))

    return render(request, 'bear_applications/version.html',
                  {'application': application, 'archs': archs, 'multideps': multideps,
                   'other_versions': other_versions, 'needs_module': needs_module, 'deprecated': deprecated,
                   'sibling_version': sibling_version, 'sibling_version_is': sibling_version_is,
                   'unsupported': unsupported, 'bav': bavname, 'cuda': cuda})


def application(request, name):
    """
    Individual application page
    """
    application = get_object_or_404(Application, name=name, reason_to_hide=None)
    versions = (application.version_set.filter(reason_to_hide=None)
                                       .values('version', 'app_sort_order',
                                               bav=F('link__bearappsversion__displayed_name'))
                                       .distinct())
    if versions.count() == 0:
        raise Http404("There are no versions of this application")
    elif versions.count() == 1 and versions[0]['version'] in SPECIAL_PAGE_NAMES:
        versions = None
    else:
        versions = sorted(versions, key=lambda k: (k['app_sort_order'], parse_version(k['version'])), reverse=True)

    return render(request, 'bear_applications/application.html', {'application': application, 'versions': versions})


def search(request):
    """
    Search page
    """
    filter_on = []
    searched = {}

    if request.GET.get('search'):
        search_on = request.GET.get('search').strip()
        searched['name'] = search_on
        filter_on.append(Q(application__name__icontains=search_on))
        filter_on.append(Q(version__icontains=search_on))
        filter_on.append(Q(application__description__icontains=search_on))
        filter_on.append(Q(module_load__icontains=search_on))
        filter_on.append(Q(paragraphdata__content__icontains=search_on))
        filter_on.append(Q(paragraphdata__header__icontains=search_on))
        filter_on.append(Q(application__paragraphdata__content__icontains=search_on))
        filter_on.append(Q(application__paragraphdata__header__icontains=search_on))
        filter_on.append(Q(application__more_info__icontains=search_on))

    if request.GET.get('name'):
        search_on = request.GET.get('name').strip()
        searched['name'] = search_on
        if request.GET.get('partial_exact') == 'partial':
            filter_on.append(Q(application__name__icontains=search_on))
        else:
            filter_on.append(Q(application__name__iexact=search_on))

    if request.GET.get('version'):
        search_on = request.GET.get('version').strip()
        searched['version'] = search_on
        if request.GET.get('partial_exact') == 'partial':
            filter_on.append(Q(version__icontains=search_on))
        else:
            filter_on.append(Q(version__iexact=search_on))

    if request.GET.get('module'):
        search_on = request.GET.get('module').strip()
        searched['module'] = search_on
        if request.GET.get('partial_exact') == 'partial':
            filter_on.append(Q(module_load__icontains=search_on))
        else:
            filter_on.append(Q(module_load__iexact=search_on))

    if request.GET.get('other'):
        other_filter_on = []
        search_on = request.GET.get('other').strip()
        searched['other'] = search_on
        if request.GET.get('partial_exact') == 'partial':
            other_filter_on.append(Q(application__description__icontains=search_on))
            other_filter_on.append(Q(paragraphdata__content__icontains=search_on))
            other_filter_on.append(Q(paragraphdata__header__icontains=search_on))
            other_filter_on.append(Q(application__paragraphdata__content__icontains=search_on))
            other_filter_on.append(Q(application__paragraphdata__header__icontains=search_on))
            other_filter_on.append(Q(application__more_info__icontains=search_on))
        else:
            other_filter_on.append(Q(application__description__iexact=search_on))
            other_filter_on.append(Q(paragraphdata__content__iexact=search_on))
            other_filter_on.append(Q(paragraphdata__header__iexact=search_on))
            other_filter_on.append(Q(application__paragraphdata__content__iexact=search_on))
            other_filter_on.append(Q(application__paragraphdata__header__iexact=search_on))
            other_filter_on.append(Q(application__more_info__iexact=search_on))
        # we have to join the other items together with an 'or'
        # otherwise when we do an 'and' search it will never match anything
        filter_on.append(reduce(operator.or_, other_filter_on))

    if request.GET.get('and_or') == 'and' or not request.GET.get('and_or'):
        searched['and_or'] = 'and'
    if request.GET.get('partial_exact') == 'partial' or not request.GET.get('partial_exact'):
        searched['partial_exact'] = 'partial'
    if request.GET.get('deprecated') == 'no':
        searched['deprecated'] = 'no'

    if len(filter_on):
        if request.GET.get('and_or') == 'and':
            filter_q = reduce(operator.and_, filter_on)
        else:
            filter_q = reduce(operator.or_, filter_on)

        appversions = (Version.objects.filter(reason_to_hide=None, application__reason_to_hide=None,
                                              link__bearappsversion__hidden=False, link__architecture__hidden=False)
                                      .filter(filter_q).distinct())
        if request.GET.get('deprecated') == 'no':
            exclude_versions = (Link.objects.filter(bearappsversion__deprecated=True)
                                            .values_list('version__id', flat=True))
            appversions = appversions.exclude(id__in=exclude_versions)
        appversions = appversions.values('app_sort_order', name=F('application__name'), ver=F('version'),
                                         bav=F('link__bearappsversion__displayed_name'))
    else:
        appversions = []

    for appver in appversions:
        bavs = Link.objects.filter(version__version=appver['ver'], version__application__name=appver['name'],
                                   bearappsversion__hidden=False, architecture__hidden=False)
        deprecated_bav_count = bavs.filter(bearappsversion__deprecated=True).count()
        unsupported_bav_count = bavs.filter(bearappsversion__supported=False).count()

        appver['deprecated'] = False
        appver['supported'] = True
        if bavs.count() == deprecated_bav_count and deprecated_bav_count > 0:
            appver['deprecated'] = True
        if bavs.count() == unsupported_bav_count and unsupported_bav_count > 0:
            appver['supported'] = False

    if appversions:
        appversions = sorted(appversions, key=lambda k: (-k['supported'], k['deprecated'], k['name'],
                                                         -k['app_sort_order']))

    return render(request, 'bear_applications/search.html',
                  {'appversions': appversions, 'searched': searched,
                   'search_deprec': settings.WEBSITE_SITE_CONFIG['DISPLAY_SEARCH_DEPREC']})


def filter(request, bearappsversion, arch=None):
    """
    Architecture and bearappsversion pages
    """
    if bearappsversion == 'all':
        architecture = get_object_or_404(Architecture, displayed_name=arch)
        if architecture.hidden or architecture.name == 'system':
            raise Http404("No Architecture matches the given query.")
        to_search = architecture.link_set.filter(version__reason_to_hide=None,
                                                 version__application__reason_to_hide=None)
        deprecated = False
        supported = True
        gpus = architecture.gpu_set.all()
    elif arch is None:
        bav = get_object_or_404(BearAppsVersion, displayed_name=bearappsversion)
        if bav.hidden or bav.name == 'system':
            raise Http404("No BEAR Application Version matches the given query.")
        to_search = bav.link_set.filter(version__reason_to_hide=None, version__application__reason_to_hide=None)
        deprecated = bav.deprecated
        supported = bav.supported
        gpus = None
    else:
        architecture = get_object_or_404(Architecture, displayed_name=arch)
        if architecture.hidden or architecture.name == 'system':
            raise Http404("No Architecture matches the given query.")
        bav = get_object_or_404(BearAppsVersion, displayed_name=bearappsversion)
        if bav.hidden or bav.name == 'system':
            raise Http404("No BEAR Application Version matches the given query.")
        to_search = Link.objects.filter(bearappsversion=bav, architecture=architecture,
                                        version__reason_to_hide=None,
                                        version__application__reason_to_hide=None)
        deprecated = bav.deprecated
        supported = bav.supported
        gpus = architecture.gpu_set.all()

    if bearappsversion == 'all':
        applications = (to_search.distinct()
                                 .filter(version__link__bearappsversion__hidden=False,
                                         version__link__architecture__hidden=False)
                                 .values(name=F('version__application__name'), ver=F('version__version'),
                                         bav=F('version__link__bearappsversion__displayed_name'))
                                 .order_by(Lower('name'), '-ver'))
    else:
        applications = (to_search.distinct()
                                 .values(name=F('version__application__name'), ver=F('version__version'),
                                         bav=Value(bearappsversion))
                                 .order_by(Lower('name'), '-ver'))

    return render(request, 'bear_applications/filter.html',
                  {'applications': applications, 'bearappsversion': bearappsversion, 'arch': arch,
                   'deprecated': deprecated, 'supported': supported, 'gpus': gpus})


def filter_options(request):
    """
    List out all options of Architecture and bearappsversion
    """
    if settings.WEBSITE_SITE_CONFIG['BAV_ORDER'] == 'asc':
        order = ''
    else:
        order = '-'

    combos = (Link.objects.filter(version__reason_to_hide=None, version__application__reason_to_hide=None,
                                  bearappsversion__hidden=False, architecture__hidden=False)
                          .exclude(bearappsversion__name='system', architecture__name='system')
                          .values(bav=F('bearappsversion__displayed_name'), arch=F('architecture__displayed_name'),
                                  deprecated=F('bearappsversion__deprecated'),
                                  supported=F('bearappsversion__supported'))
                          .annotate(bav_order=Case(When(bav__endswith='h', then=Value(1)), default=Value(0),
                                                   output_field=IntegerField()))
                          .annotate(bav_year=Substr('bav', 1, 4))
                          .distinct().order_by(f'{order}bav_year', 'bav_order', f'{order}bav'))
    bearappversions = (Link.objects.filter(version__reason_to_hide=None, version__application__reason_to_hide=None,
                                           bearappsversion__hidden=False)
                                   .exclude(bearappsversion__name='system', architecture__name='system')
                                   .values(bav=F('bearappsversion__displayed_name'),
                                           deprecated=F('bearappsversion__deprecated'),
                                           supported=F('bearappsversion__supported'))
                                   .annotate(bav_order=Case(When(bav__endswith='h', then=Value(1)), default=Value(0),
                                                            output_field=IntegerField()))
                                   .annotate(bav_year=Substr('bav', 1, 4))
                                   .distinct().order_by(f'{order}bav_year', 'bav_order', f'{order}bav'))
    architectures = (Link.objects.filter(version__reason_to_hide=None, version__application__reason_to_hide=None,
                                         bearappsversion__hidden=False, architecture__hidden=False)
                                 .exclude(bearappsversion__name='system', architecture__name='system')
                                 .values(arch=F('architecture__displayed_name'))
                                 .distinct().order_by('arch'))

    if not settings.WEBSITE_SITE_CONFIG['DISPLAY_ARCH']:
        combos = []
        architectures = []

    return render(request, 'bear_applications/filter_options.html',
                  {'bearappversions': bearappversions, 'architectures': architectures, 'combos': combos})


def home(request):
    """
    Home page
    """
    recent = (Version.objects.filter(reason_to_hide=None, application__reason_to_hide=None)
                             .order_by('-modified')[:10])
    application_count = CurrentVersion.objects.filter(version__reason_to_hide=None,
                                                      version__application__reason_to_hide=None).count()
    return render(request, f"bear_applications/{settings.WEBSITE_SITE_CONFIG['HOME_PAGE']}",
                  {'recent': recent, 'application_count': application_count})
