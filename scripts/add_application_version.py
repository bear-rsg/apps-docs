#!venv/bin/python
from functions import abort, set_up_logging, upload_data
import datetime
import pytz

import logging
logger = logging.getLogger()


def add_appver(app, ver, modload, home, desc, bav):
    """
    Add this application version directly to the website

    @param app: application name
    @param ver: version string
    @param modload: module load command
    """
    timezone = pytz.timezone("Europe/London")
    created = timezone.localize(datetime.datetime.now())
    modified = created

    if 'module load' in modload:
        abort("Please don't include 'module load' in your module load command")

    # Presume intel only:
    upload_data(app, ver, None, bav, modload, home, desc, created, modified)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Add info from a module to the bear_apps_docs database')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('application', help='Application name')
    parser.add_argument('version', help='Version name')
    parser.add_argument('bav', help='BEAR Apps Version name')
    parser.add_argument('module', help='Module load command (without the "module load")')
    parser.add_argument('home', help='Home page URL')
    parser.add_argument('desc', help='Description')
    args = parser.parse_args()

    set_up_logging(args.debug)

    add_appver(args.application, args.version, args.module, args.home, args.desc, args.bav)
