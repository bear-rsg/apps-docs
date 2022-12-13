#!venv/bin/python
import logging
from functions import set_up_logging
from bear_applications.models import Link, Architecture


logger = logging.getLogger(__name__)


def delete(arch):
    """
    Delete all mentions of this architecture
    """
    arch_obj = Architecture.objects.get(name=arch)

    for link in Link.objects.filter(architecture=arch_obj):
        print("DELETING link %s/%s/%s/%s" % (link.version.application.name, link.version.version,
                                             link.bearappsversion.name, link.architecture.name))
        link.delete()
        ver_links = Link.objects.filter(version=link.version)
        print(" * %s" % (', '.join("%s:%s" % (x.bearappsversion.name, x.architecture.name) for x in ver_links)))
        if not ver_links:
            print("DELETING %s/%s" % (link.version.application.name, link.version.version))
            link.version.delete()

    arch_obj.delete()
    return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Delete an application, or version, from the database')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('--arch', help='Architecture version, e.g. EL7-sandybridge', required=True)

    args = parser.parse_args()

    set_up_logging(args.debug)

    delete(arch=args.arch)
