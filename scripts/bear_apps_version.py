#!venv/bin/python
import logging
from functions import abort, set_up_logging
from bear_applications.models import BearAppsVersion

logger = logging.getLogger(__name__)


def mark_deprecated(*, bear_application_version):
    """
    Mark a BEAR Application version as deprecated
    """
    bear_application_version.deprecated = True
    bear_application_version.save()
    logger.info("BEAR Application Version %s marked as deprecated", bear_application_version.displayed_name)


def mark_not_deprecated(*, bear_application_version):
    """
    Mark a BEAR Application version as not deprecated
    """
    bear_application_version.deprecated = False
    bear_application_version.save()
    logger.info("BEAR Application Version %s marked as not deprecated", bear_application_version.displayed_name)


def mark_supported(*, bear_application_version):
    """
    Mark a BEAR Application version as supported
    """
    bear_application_version.supported = True
    bear_application_version.save()
    logger.info("BEAR Application Version %s marked as deprecated", bear_application_version.displayed_name)


def mark_not_supported(*, bear_application_version):
    """
    Mark a BEAR Application version as not supported
    """
    bear_application_version.supported = False
    bear_application_version.save()
    logger.info("BEAR Application Version %s marked as not supported", bear_application_version.displayed_name)


def mark_auto_loaded(*, bear_application_version):
    """
    Mark a BEAR Application version as automatically loaded by default
    """
    bear_application_version.auto_loaded = True
    bear_application_version.save()
    logger.info("BEAR Application Version %s marked as loaded by default", bear_application_version.displayed_name)


def mark_not_auto_loaded(*, bear_application_version):
    """
    Mark a BEAR Application version as not automatically loaded by default
    """
    bear_application_version.auto_loaded = False
    bear_application_version.save()
    logger.info("BEAR Application Version %s marked as not loaded by default", bear_application_version.displayed_name)


def set_visibility(*, bear_application_version, hidden):
    """
    Set BEAR Application version visiblility
    """
    bear_application_version.hidden = hidden
    bear_application_version.save()
    logger.info("BEAR Application Version %s marked as %s", bear_application_version.displayed_name,
                'hidden' if hidden else 'visible')


def list_bavs(args):
    """
    List existing BEAR Application Versions
    """
    for bav in BearAppsVersion.objects.all().order_by('name'):
        print("{} : {} : {}, {}, {}, {}".format(
            bav.name,
            bav.displayed_name,
            'Supported' if bav.supported else 'Unsupported',
            'Deprecated' if bav.deprecated else 'Not deprecated',
            'Autoloaded' if bav.auto_loaded else 'Not autoloaded',
            'Hidden' if bav.hidden else 'Visible'))


def modify_bav(args):
    """
    Modify a BEAR Application Version
    """
    try:
        bear_application_version = BearAppsVersion.objects.get(name=args.bear_application_version)
    except BearAppsVersion.DoesNotExist:
        abort("Can't find BEAR Application Version %s" % args.bear_application_version)

    if args.not_auto_loaded:
        mark_not_auto_loaded(bear_application_version=bear_application_version)
    elif args.auto_loaded:
        mark_auto_loaded(bear_application_version=bear_application_version)
    if args.deprecated:
        mark_deprecated(bear_application_version=bear_application_version)
    elif args.undeprecated:
        mark_not_deprecated(bear_application_version=bear_application_version)
    if args.supported:
        mark_supported(bear_application_version=bear_application_version)
    elif args.unsupported:
        mark_not_supported(bear_application_version=bear_application_version)
    if args.hidden:
        set_visibility(bear_application_version=bear_application_version, hidden=True)
    elif args.visible:
        set_visibility(bear_application_version=bear_application_version, hidden=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Modify a BEAR Application Version')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list = subparsers.add_parser('list', help='List BEAR Application Versions')
    parser_list.set_defaults(func=list_bavs)

    parser_modify = subparsers.add_parser('modify', help='Modify a BEAR Application Version')
    parser_modify.set_defaults(func=modify_bav)
    parser_modify.add_argument('bear_application_version', help='BEAR Application Version')
    parser_modify.add_argument('--not-auto-loaded', action='store_true', help='Mark as not auto loaded')
    parser_modify.add_argument('--auto-loaded', action='store_true', help='Mark as auto loaded')
    parser_modify.add_argument('--deprecated', action='store_true', help='Mark as deprecated')
    parser_modify.add_argument('--undeprecated', action='store_true', help='Mark as not deprecated')
    parser_modify.add_argument('--supported', action='store_true', help='Mark as supported')
    parser_modify.add_argument('--unsupported', action='store_true', help='Mark as not supported')
    parser_modify.add_argument('--hidden', action='store_true', help='Mark as hidden')
    parser_modify.add_argument('--visible', action='store_true', help='Mark as visible')

    args = parser.parse_args()
    set_up_logging(args.debug)
    args.func(args)
