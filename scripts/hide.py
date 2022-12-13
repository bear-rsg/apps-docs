#!venv/bin/python
import os
import logging
import time
from functions import abort, get_application, set_up_logging
from bear_applications.models import Application, Link, Version


logger = logging.getLogger(__name__)


def _hide_obj(*, obj_to_hide, reason):
    """
    Hide this object with the given reason
    """
    try:
        me = os.environ['USER']
    except KeyError:
        abort("Unable to identify user from environment (looked for USER in env)")

    obj_to_hide.reason_to_hide = "[%s] [%s] %s" % (time.ctime(), me, reason)
    obj_to_hide.save()
    if isinstance(obj_to_hide, Application):
        hidden = "Application {}".format(obj_to_hide.name)
    elif isinstance(obj_to_hide, Version):
        hidden = "Version {} of {}".format(obj_to_hide.version, obj_to_hide.application.name)
    logger.info("%s hidden, with reason %s", hidden, reason)


def hide_app(args):
    """
    Hide an application recording the given reason.

    This expects args to have the following attributes:
    - args.application (str): Name of the application to hide
    - args.reason (str): Reason for hiding the application
    """
    app, _ = get_application(args.application, None)
    versions = Version.objects.filter(application=app)
    for ver in versions:
        _hide_obj(obj_to_hide=ver, reason=args.reason)
    _hide_obj(obj_to_hide=app, reason=args.reason)


def hide_ver(args):
    """
    Hide a version of an application recording the given reason.

    This expects args to have the following attributes:
    - args.application (str): Name of the application to hide
    - args.version (str): Name of the version to hide
    - args.reason (str): Reason for hiding the application
    """
    _, ver = get_application(args.application, args.version)
    _hide_obj(obj_to_hide=ver, reason=args.reason)


def hide_versions_with_no_visible_links(args):
    """
    Hide all versions where there are no visible links (i.e. installed for old BAVs or archs only).
    Do not hide if version is 'Information Page' (OpenFOAM and Singularity)

    This expects args to have the following attributes:
    - args.reason (str): Reason for hiding the application
    """
    vers = Version.objects.filter(reason_to_hide=None).exclude(version='Information Page').order_by('application__name',
                                                                                                    'version')
    for ver in vers:
        if ver.application.name == 'Java' and ver.version in ['1.8', '11']:
            continue

        visible_links = Link.objects.filter(version=ver, architecture__hidden=False, bearappsversion__hidden=False)
        if visible_links.count() == 0:
            _hide_obj(obj_to_hide=ver, reason=args.reason)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Hide applications or versions from display')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_hide_versions_no_visible_links = subparsers.add_parser('hide_vers',
                                                                  help='Hide all versions with no visible links')
    parser_hide_versions_no_visible_links.set_defaults(func=hide_versions_with_no_visible_links)
    parser_hide_versions_no_visible_links.add_argument('reason', help='Reason for hiding this application')

    parser_app = subparsers.add_parser('app', help='Hide an application')
    parser_app.set_defaults(func=hide_app)
    parser_app.add_argument('application', help='Application')
    parser_app.add_argument('reason', help='Reason for hiding this application')

    parser_ver = subparsers.add_parser('ver', help='Hide a version of an application')
    parser_ver.set_defaults(func=hide_ver)
    parser_ver.add_argument('application', help='Application')
    parser_ver.add_argument('version', help='Version')
    parser_ver.add_argument('reason', help='Reason for hiding this version')

    args = parser.parse_args()
    set_up_logging(args.debug)
    args.func(args)
