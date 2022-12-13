#!venv/bin/python
import logging
from packaging.version import parse as parse_version
from functions import abort, get_application, set_up_logging

from bear_applications.models import Version

logger = logging.getLogger(__name__)


def rename_application(*, application, newname):
    """
    Rename an application
    """
    oldname = application.name
    application.name = newname
    application.save()

    logger.info("Renamed %s to %s", oldname, newname)


def change_more_information(*, application, link):
    """
    Change the more info link
    """
    application.more_info = link
    application.save()

    logger.info("More info link for %s changed to %s", application.name, link)


def change_description(*, application, filename):
    """
    Change the description of the application
    """
    try:
        with open(filename) as f:
            content = f.read()
    except IOError as e:
        abort("Error (%s) reading %s" % (e, filename))

    application.description = content
    application.save()

    logger.info("Changed description for %s", application.name)


def show_order(*, application):
    """
    Show the order of the versions of the application
    """
    logger.info("Application: %s", application.name)
    versions = Version.objects.filter(application=application, reason_to_hide=None)
    versions = sorted(versions, key=lambda k: (k.app_sort_order, parse_version(k.version)), reverse=True)
    for ver in versions:
        logger.info("    %s (%s)", ver.version, ver.app_sort_order)


def get_description(*, application):
    """
    Get the description
    """
    logger.info("The description for %s is\n%s", application, application.description)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Modify an application')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-a', '--application', help='Application name', required=True)
    parser.add_argument('-n', '--newname', help='Rename the application')
    parser.add_argument('-l', '--link', help='Change the more info link')
    parser.add_argument('-D', '--description', action='store_true',
                        help='Get or change the description. If changing the description then a filename is required')
    parser.add_argument('-f', '--filename', help='Filename containing the HTML-formatted paragraph to add')
    parser.add_argument('-o', '--order', action='store_true',
                        help='Show the sort order of the versions of this application')

    args = parser.parse_args()

    set_up_logging(args.debug)

    app, _ = get_application(args.application)

    if args.newname:
        rename_application(application=app, newname=args.newname)
    elif args.link:
        change_more_information(application=app, link=args.link)
    elif args.description and args.filename:
        change_description(application=app, filename=args.filename)
    elif args.description:
        get_description(application=app)
    elif args.order:
        show_order(application=app)
    else:
        abort("There was a problem with the options")
