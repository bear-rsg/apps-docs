#!venv/bin/python
import logging
from functions import set_up_logging
from bear_applications.models import Link, BearAppsVersion


logger = logging.getLogger(__name__)


def delete(bav, delete_versions=True):
    """
    Delete all mentions of this bear apps version
    """
    bav_obj = BearAppsVersion.objects.get(name=bav)
    for link in Link.objects.filter(bearappsversion=bav_obj):
        print("DELETING link %s/%s/%s/%s" % (link.version.application.name, link.version.version,
                                             link.bearappsversion.name, link.architecture.name))
        link.delete()
        if delete_versions:
            ver_links = Link.objects.filter(version=link.version)
            print(" * %s" % (', '.join("%s:%s" % (x.bearappsversion.name, x.architecture.name) for x in ver_links)))
            if not ver_links:
                print("DELETING %s/%s" % (link.version.application.name, link.version.version))
                link.version.delete()

    bav_obj.delete()
    return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Delete an application, or version, from the database')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('--links-only', help='Only delete the links', action='store_true')
    parser.add_argument('-b', '--bear_application_version', help='BEAR Application Version', required=True)

    args = parser.parse_args()

    set_up_logging(args.debug)

    delete(bav=args.bear_application_version, delete_versions=not args.links_only)
