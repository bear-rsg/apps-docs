#!venv/bin/python
import logging
from functions import set_up_logging
from django.db.models import Count
from bear_applications.models import Application, CurrentVersion, Version

logger = logging.getLogger(__name__)


def no_versions():
    """
    Identify applications with no versions
    """
    logger.info("Looking for application with no versions")
    apps = Application.objects.annotate(ver_count=Count('version')).filter(ver_count=0)
    for app in apps:
        logger.info("%s", app.name)


def no_links():
    """
    Identify visibile Versions with no Links (i.e. no arch / BAV combos)
    """
    logger.info("Looking for versions with no links set")
    ignore_list = ['Java', 'OpenFOAM', 'Singularity']
    logger.info("  These are not checked for having no links: %s", ', '.join(ignore_list))
    vers = Version.objects.filter(reason_to_hide=None, application__reason_to_hide=None)
    vers = vers.exclude(application__name__in=ignore_list)
    for ver in vers:
        if ver.link_set.filter(bearappsversion__hidden=False).count() == 0:
            logger.info("  %s - %s", ver.application.name, ver.version)


def versions():
    """
    Identify Applications with no or multiple current versions set, or no visible versions
    """
    logger.info("Looking for applications with no current version, multiple current versions, GPU toolchain current "
                "version, or current version in deprecated or hidden")
    apps = Application.objects.filter(reason_to_hide=None).order_by('name')
    for app in apps:
        ver_count = Version.objects.filter(application=app, reason_to_hide=None).count()
        if ver_count > 0:
            cvs = CurrentVersion.objects.filter(application=app)
            cv_active = []
            cv_inactive = []
            cv_deprec = []

            for cv in cvs:
                if cv.version.reason_to_hide:
                    cv_inactive.append(cv)
                else:
                    cv_active.append(cv)

                if cv.version.link_set.filter(bearappsversion__deprecated=True).count() > 0:
                    cv_deprec.append(cv)

                gpucv = False
                for gputoolchain in ['-gompic-', '-fosscuda-', '-iomklc-', '-iompic-']:
                    if gputoolchain in cv.version.version:
                        gpucv = True
                if gpucv:
                    logger.info("  GPU Toolchain current version: %s", app.name)

            if len(cv_active) == 0:
                logger.info("  No current version: %s", app.name)
            elif len(cv_active) > 1:
                logger.info("  Multiple current versions: %s", app.name)
                for cv in cv_active:
                    logger.info("    %s", cv.version.version)

            if len(cv_inactive) > 0:
                logger.info("  Inactive current version: %s", app.name)
                for cv in cv_inactive:
                    logger.info("    %s", cv.version.version)

            if len(cv_deprec) > 0:
                logger.info("  Deprec current version: %s", app.name)
                for cv in cv_deprec:
                    logger.info("    %s", cv.version.version)

                alts = cv.application.version_set.filter(reason_to_hide=None, application__reason_to_hide=None)
                possible_alts = []
                for alt in alts:
                    if alt.link_set.filter(bearappsversion__deprecated=False, bearappsversion__hidden=False,
                                           architecture__hidden=False).count() > 0:
                        possible_alts.append(alt)
                if len(possible_alts) > 0:
                    logger.info("    Alternatives:")
                    for alt in possible_alts:
                        logger.info("        %s", alt.version)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Identify Problems')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-l', '--no-links', action='store_true', help='Versions with no links')
    parser.add_argument('-c', '--versions', action='store_true',
                        help='Applications with no, or multiple, current versions set or with no visible versions')
    parser.add_argument('-p', '--applications', action='store_true', help='Applications with no versions')
    parser.add_argument('-a', '--all', action='store_true', help='Run all checks')

    args = parser.parse_args()
    set_up_logging(args.debug)

    if args.no_links or args.all:
        no_links()

    if args.versions or args.all:
        versions()

    if args.applications or args.all:
        no_versions()
