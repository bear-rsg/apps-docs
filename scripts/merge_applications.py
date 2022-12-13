#!venv/bin/python
from functions import abort, get_application, set_up_logging
import framework  # NOQA
import logging
import os
import time
from bear_applications.models import Version, CurrentVersion

logger = logging.getLogger(__name__)


def rename_application(*, oldname, newname):
    """
    Rename an application
    """
    try:
        me = os.environ['USER']
    except KeyError:
        abort("Unable to identify user from environment (looked for USER in env)")

    oldapplication, _ = get_application(oldname)
    newapplication, _ = get_application(newname)

    to_merge = Version.objects.filter(application=oldapplication)

    for v in to_merge:
        v.application = newapplication
        v.save()
        logger.info("moved %s from %s to %s", v.version, oldname, newname)

    cv = CurrentVersion.objects.filter(application=oldapplication)

    for v in cv:
        logger.info("delete %s as %s current version", v.version.version, oldname)
        v.delete()

    reason = "merged %s into %s" % (oldname, newname)
    oldapplication.reason_to_hide = "[%s] [%s] %s" % (time.ctime(), me, reason)
    oldapplication.save()
    logger.info("%s hidden, with reason %s", oldapplication.name, reason)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Merge all versions of one application into another')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-o', '--oldname', help='Old application name', required=True)
    parser.add_argument('-n', '--newname', help='New application name', required=True)

    args = parser.parse_args()

    set_up_logging(args.debug)

    rename_application(oldname=args.oldname, newname=args.newname)
