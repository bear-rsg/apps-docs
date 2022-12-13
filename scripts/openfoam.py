#!venv/bin/python
import logging
from argparse import Namespace
from functions import get_application, set_up_logging
from current_version import set_current_version

logger = logging.getLogger(__name__)

OPENFOAM_APPLICATION_NAME = 'OpenFOAM'
OPENFOAM_INFORMATION_PAGE = 'Information Page'


def move_new_version(*, target_openfoam, version, set_as_current):
    """
    Move the new OpenFOAM to this type of OpenFOAM
    """
    target_openfoam_obj, _ = get_application(target_openfoam)
    _, new_version = get_application(OPENFOAM_APPLICATION_NAME, version)
    new_version.application = target_openfoam_obj
    new_version.save()
    logger.info("Moved %s to %s", new_version.version, target_openfoam)

    if set_as_current:
        args = Namespace(application=target_openfoam, version=version)
        set_current_version(args)
        logger.info("Set %s as current version for %s", new_version.version, target_openfoam)

    args = Namespace(application=OPENFOAM_APPLICATION_NAME, version=OPENFOAM_INFORMATION_PAGE)
    set_current_version(args)
    logger.info("Reset OpenFOAM Information Page as current version")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Sort out a new OpenFOAM')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-o', '--openfoam', help='OpenFoam Type', required=True)
    parser.add_argument('-v', '--version', help='Version name', required=True)
    parser.add_argument('-s', '--set_as_current', action='store_true', help='Set new version as current version')

    args = parser.parse_args()

    set_up_logging(args.debug)

    move_new_version(target_openfoam=args.openfoam, version=args.version, set_as_current=args.set_as_current)
