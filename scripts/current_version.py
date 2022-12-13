#!venv/bin/python
from functions import get_application, set_up_logging
import framework  # NOQA
import logging
from bear_applications.models import CurrentVersion, Version

logger = logging.getLogger(__name__)


def set_current_version(args):
    """
    Set the current version of an application. This will remove whatever is currently set.

    This expects args to have the following attributes:
    - args.application (str): Name of the application to hide
    - args.version (str): Name of the version to hide
    """
    app, ver = get_application(args.application, args.version)

    # there should only be one, but we'll protect against there being multiple by using filter
    current_version = CurrentVersion.objects.filter(application=app)

    for cv in current_version:
        logger.info("Unset version %s", cv.version.version)
        cv.delete()

    cv = CurrentVersion()
    cv.application = app
    cv.version = ver
    cv.save()

    logger.info("%s set as current version for %s", ver.version, app.name)


def list_versions(args):
    """
    List versions, marked current version if set

    This expects args to have the following attributes:
    - args.application (str): Name of the application to hide
    """
    app, _ = get_application(args.application, version=None)

    for ver in Version.objects.filter(application=app):
        logger.info("%s%s", ver.version,
                    " *" if CurrentVersion.objects.filter(application=app, version=ver).exists() else "")


def remove_current_version(args):
    """
    Remove the current version for application

    This expects args to have the following attributes:
    - args.application (str): Name of the application to hide
    """
    app, _ = get_application(args.application, version=None)
    current_version = CurrentVersion.objects.filter(application=app)
    for cv in current_version:
        logger.info("Unset version %s for %s", cv.version.version, cv.application.name)
        cv.delete()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Current Version')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list = subparsers.add_parser('list', help='List versions for application')
    parser_list.set_defaults(func=list_versions)
    parser_list.add_argument('application', help='Application')

    parser_set = subparsers.add_parser('modify', help='Modify a current version')
    parser_set.set_defaults(func=set_current_version)
    parser_set.add_argument("application", help="Application")
    parser_set.add_argument("version", help="Version to set as current")

    parser_remove = subparsers.add_parser('remove', help='Remove current version')
    parser_remove.set_defaults(func=remove_current_version)
    parser_remove.add_argument("application", help="Application")

    args = parser.parse_args()
    set_up_logging(args.debug)
    args.func(args)
