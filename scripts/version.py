#!venv/bin/python
import logging
from functions import abort, get_application, set_up_logging

logger = logging.getLogger(__name__)


def rename_version(*, version, newname):
    """
    Rename a version
    """
    oldname = version.version
    version.version = newname
    version.save()

    logger.info("Renamed %s %s to %s", version.application.name, oldname, newname)


def change_module_load(*, version, module_load):
    """
    Change the module load command
    """
    oldmodule = version.module_load
    version.module_load = module_load
    version.save()

    logger.info("Module load for %s %s changed from %s to %s",
                version.application.name, version.version, oldmodule, module_load)


def change_app_sort_order(*, version, order):
    """
    Change the sort order of this version of the application
    """
    oldorder = version.app_sort_order
    version.app_sort_order = order
    version.save()

    logger.info("For %s / %s the sort order has changed from %s to %s",
                version.application.name, version.version, oldorder, order)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Modify a version')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-a', '--application', help='Application name', required=True)
    parser.add_argument('-v', '--version', help='Version name', required=True)
    parser.add_argument('-n', '--newname', help='Rename the version')
    parser.add_argument('-m', '--module', help='Change the module load command')
    parser.add_argument('-o', '--order', help='Change the application sort order of this version', type=int)

    args = parser.parse_args()

    set_up_logging(args.debug)

    _, ver = get_application(args.application, args.version)

    if args.newname:
        rename_version(version=ver, newname=args.newname)
    elif args.module:
        change_module_load(version=ver, module_load=args.module)
    elif args.order is not None:
        change_app_sort_order(version=ver, order=args.order)
    else:
        abort("There was a problem with the options")
