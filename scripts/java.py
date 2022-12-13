#!venv/bin/python
import datetime
import logging
import pytz
from functions import abort, set_up_logging
from bear_applications.models import Application, Architecture, BearAppsVersion, Link, Version

logger = logging.getLogger(__name__)


def java_wrapper(version, bav=None, arch=None):
    """
    Java wrapper for version in bav / arch
    If bav / arch is not defined then we'll do all bavs / archs
    """
    app = Application.objects.get(name='Java')

    if bav:
        bavs = BearAppsVersion.objects.filter(displayed_name=bav)
    else:
        bavs = BearAppsVersion.objects.filter(hidden=False)

    if arch:
        archs = Architecture.objects.filter(displayed_name=arch)
    else:
        archs = Architecture.objects.filter(hidden=False)

    if archs.count() == 0 or bavs.count() == 0:
        abort("Problem finding BAVs or Archs")

    try:
        ver = Version.objects.get(application=app, version=version)
    except Version.DoesNotExist:
        now = datetime.datetime.now(pytz.timezone('Europe/London'))
        ver = Version.objects.create(
            application=app, version=version, module_load=f'Java/{version}', created=now, modified=now
        )
        logger.info("Added Java %s", version)

    for bav in bavs:
        for arch in archs:
            Link.objects.create(version=ver, bearappsversion=bav, architecture=arch)
            logger.info("  Added %s - %s", bav.displayed_name, arch.displayed_name)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Populate a Java')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('version', help='Version name')
    parser.add_argument('-b', '--bav', help='BEAR Apps Version. If undefined then does all BAVs.')
    parser.add_argument('-a', '--arch', help='Architecture. If undefined then does all archs.')

    args = parser.parse_args()

    set_up_logging(args.debug)

    java_wrapper(args.version, bav=args.bav, arch=args.arch)
