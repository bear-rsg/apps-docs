#!venv/bin/python
from functions import set_up_logging, upload_data, abort
import re
import os
import datetime
import pytz

import logging
logger = logging.getLogger()


# For parsing the module contents
re_homepage = re.compile(r"module-whatis \{Homepage:(.*?)\}")
re_description = re.compile(r"module-whatis \{Description:(.*?)\}", re.DOTALL)
re_extensions = re.compile(r"module-whatis \{Extensions:(.*?)\}", re.DOTALL)
re_multideps = re.compile(r"module-whatis \{Compatible modules:(.*?)\}", re.DOTALL)
re_dependencies = re.compile(r"^\s*module load *(.*?)\s*\n", re.MULTILINE)

# For parsing the filename
if os.path.exists("/bask/apps"):
    re_filename_eb = re.compile(r"^/bask/apps/([^/]+)/([^/]+)/modules/all/([^/]+)/(.*)$")
else:
    re_filename_eb = re.compile(r"^/rds/bear-apps/([^/]+)/([^/]+)/modules/all/([^/]+)/(.*)$")


def add_module(module_file, skip_deps):
    """
    Add info from this module file (TCL) to the database - unless
    it already exists.

    @param module_file: (txt) full path filename
    """
    with open(module_file) as f:
        tcl = f.read()

    data = {}
    for vbl, regex in [('home', re_homepage),
                       ('desc', re_description),
                       ('ext', re_extensions)]:
        try:
            data[vbl] = regex.findall(tcl)[0].strip()
        except Exception:
            logger.info("Couldn't get %s", vbl)

    if skip_deps:
        data['deps'] = None
    else:
        try:
            data['deps'] = re_dependencies.findall(tcl)
            multideps = re_multideps.findall(tcl)[0].replace(',', '').split()
            for dep in multideps:
                if '(default)' not in dep:
                    data['deps'].append(dep.strip())
        except Exception as e:
            logger.info(f"Couldn't get deps with exception: {repr(e)}")

    filename_match = re_filename_eb.match(module_file)
    if filename_match:
        data['bav_family'] = filename_match.group(1)
        data['arch'] = filename_match.group(2)
        data['name'] = filename_match.group(3)
        data['version'] = filename_match.group(4)
        data['module_load'] = '%s/%s' % (data['name'], data['version'])

    timezone = pytz.timezone("Europe/London")
    stat = os.stat(module_file)
    data['created'] = timezone.localize(datetime.datetime.fromtimestamp(stat.st_ctime))
    data['modified'] = timezone.localize(datetime.datetime.fromtimestamp(stat.st_mtime))

    try:
        upload_data(**data)
    except Exception as e:
        abort("Unable to upload data for {}. Error: {}".format(module_file, e))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Add info from a module to the bear_apps_docs database')
    parser.add_argument('-v', '--verbose', action='store_true', help='Turn on debugging output')
    parser.add_argument('-s', '--skip-deps', action='store_true', help='Skip adding dependency relationships')
    parser.add_argument('module_file', help='Full path to the module file')
    args = parser.parse_args()

    set_up_logging(args.verbose)

    if args.module_file:
        add_module(args.module_file, args.skip_deps)
