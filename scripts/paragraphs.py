#!venv/bin/python
import logging
from django.db.models import Q
from functions import abort, get_application, set_up_logging
from bear_applications.models import ParagraphData

logger = logging.getLogger(__name__)


def para_filter(*, application, version=None, header=None):
    """
    Prepare the paragraph(/s) filter for this application (all versions), or for an optional version,
    or with a specific header
    """
    app, ver = get_application(application, version)

    # We only set one of application and version on the para
    if ver:
        filter_q = Q(version=ver)
    else:
        filter_q = Q(application=app)

    if header:
        filter_q = filter_q & Q(header=header)

    return filter_q


def list_para(*, application, version=None, header=None):
    """
    List paragraph(/s) for this application (all versions), or for an optional version,
    or with a specific header
    """
    paras = ParagraphData.objects.filter(para_filter(application=application, version=version, header=header))

    for para in paras:
        logger.info("Paragraph header: %s", para.header)
        logger.info("Paragraph content:\n%s", para.content)
        logger.info("===============================")

    logger.info("Listed paragraph for to %s / %s", application, version)


def _save_para(para_obj, header, filename):
    """
    Set the header and content of this paragraph object, and save it
    """
    try:
        with open(filename) as f:
            content = f.read()
    except IOError as e:
        abort("Error (%s) reading %s" % (e, filename))

    para_obj.content = content
    para_obj.header = header
    para_obj.save()


def add_para(*, application, header, filename, version=None):
    """
    Add a paragraph to this application (all versions) or to an optional version

    The given file will be read and its contents used as the paragraph

    The header will be used as you might expect
    """
    app, ver = get_application(application, version)

    para = ParagraphData()

    # We only set one of application and version on the para
    if ver:
        para.version = ver
    else:
        para.application = app

    _save_para(para, header, filename)

    logger.info("Added paragraph for %s / %s / %s", application, version, header)


def replace_para(*, application, header, filename, version=None, newheader=None):
    """
    Replace the paragraph with the specified header for this application, or for an optional version
    The new content for the paragraph is from filename and the header can also be replaced
    """
    try:
        para = ParagraphData.objects.get(para_filter(application=application, version=version, header=header))
    except ParagraphData.DoesNotExist:
        abort("N no paragraph matched the search")

    _save_para(para, newheader if newheader else header, filename)

    logger.info("Replaced paragraph for %s / %s / %s", application, version, header)


def remove_para(*, application, header, version=None):
    """
    Remove the paragraph with the specified header for this application, or for an optional version
    """
    try:
        para = ParagraphData.objects.get(para_filter(application=application, version=version, header=header))
    except ParagraphData.DoesNotExist:
        abort("No paragraph matched the search")

    para.delete()

    logger.info("Deleted paragraph for %s / %s / %s", application, version, header)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='List paragraph data for an app or version')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-a', '--application', help='Application to add_para', required=True)
    parser.add_argument('-v', '--version', help='Application version to add_para (optional)')
    parser.add_argument('-t', '--title', help='Header of the paragraph (optional)')
    parser.add_argument('-A', '--add', action='store_true', help='Add a new paragraph (requires --filename)')
    parser.add_argument('-l', '--list', action='store_true', help='List paragraph(/s) (optional)')
    parser.add_argument('-e', '--edit', action='store_true', help='Replace the paragraph (requires --filename)')
    parser.add_argument('-n', '--newtitle', help='New header of the paragraph (optional)')
    parser.add_argument('-r', '--remove', action='store_true', help='Remove the paragraph')
    parser.add_argument('-f', '--filename', help='Filename containing the HTML-formatted paragraph to add')

    args = parser.parse_args()

    set_up_logging(args.debug)

    if (args.edit or args.remove or args.add) and not args.title:
        abort("Replacing, deleting, or adding a paragraph requires a paragraph title")

    if (args.edit or args.add) and not args.filename:
        abort("Adding or editing a paragraph requires a filename")

    if args.list:
        list_para(application=args.application, version=args.version, header=args.title)
    elif args.add:
        add_para(application=args.application, version=args.version, header=args.title, filename=args.filename)
    elif args.edit:
        replace_para(application=args.application, version=args.version, header=args.title, filename=args.filename,
                     newheader=args.newtitle)
    elif args.remove:
        remove_para(application=args.application, version=args.version, header=args.title)
    else:
        abort("There was a problem with the options")
