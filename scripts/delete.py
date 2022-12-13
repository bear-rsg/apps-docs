#!venv/bin/python
import logging
from functions import get_application, set_up_logging
from bear_applications.models import Application, Version


logger = logging.getLogger(__name__)


def _delete_obj(*, obj_to_delete):
    """
    Delete this object
    """
    obj_to_delete.delete()
    if isinstance(obj_to_delete, Version):
        logger.info("%s deleted", obj_to_delete.version)
    elif isinstance(obj_to_delete, Application):
        logger.info("%s deleted", obj_to_delete.name)


def delete(*, application, version=None):
    """
    Delete an application or a version of an application
    """
    app, ver = get_application(application, version)

    print("WARNING: This will permanently delete %s (%s)" % (application, version if version else 'all versions'))
    ok = input('OK? [y/N] ')
    if ok.lower() != 'y':
        logger.info("Aborting")
        return

    if ver:
        _delete_obj(obj_to_delete=ver)
    else:
        versions = Version.objects.filter(application=app)
        for ver in versions:
            _delete_obj(obj_to_delete=ver)
        _delete_obj(obj_to_delete=app)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Delete an application, or version, from the database')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-a', '--application', help='Application to delete', required=True)
    parser.add_argument('-v', '--version', help='Application version to delete (optional)')

    args = parser.parse_args()

    set_up_logging(args.debug)

    delete(application=args.application, version=args.version)
