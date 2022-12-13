#!venv/bin/python
import os
import logging
from functools import lru_cache
from functions import set_up_logging
from bear_applications.models import Link

logger = logging.getLogger(__name__)

BASE_PATH = "/bask/apps/system/software/lmod/hide/"
GCCCORE = 'GCCcore'
ENV = 'live'


@lru_cache(maxsize=None)
def recursive_depends_on(mod, search_dep):
    """ Recurse dependencies for mod and check if search_dep is included """
    if mod == search_dep:
        return True
    for dep in mod.dependencies.all():
        if search_dep == dep or recursive_depends_on(dep, search_dep):
            return True
    return False


def main():
    """
    For every GCCcore version generate a hide file for Lmod by:
      * looping over all modules in ENV
      * adding those that do not have that GCCcore as a dep (direct or indirect) to the file
    Baskerville Portal JupyterLab uses the correct file to hide incompatible modules

    NOTE: This will hide modules that don't have a GCCcore dep at all. This is fine for now, but may need
    revisiting later, or we might wish to whitelist certain modules etc.
    """
    all_items = Link.objects.filter(bearappsversion__name=ENV).order_by('version__application__name')
    logger.info("There are %d modules in the %s environment", all_items.count(), ENV)

    for gcc in Link.objects.filter(version__application__name=GCCCORE, bearappsversion__name=ENV):
        gcc = Link.objects.get(version__application__name=GCCCORE, version__version=gcc.version.version,
                               bearappsversion__name=ENV)

        count = 0
        filename = os.path.join(BASE_PATH, f"gcc{gcc.version.version}.lua")
        with open(filename, 'w') as f:
            for item in all_items:
                if not recursive_depends_on(item.version, gcc.version):
                    count += 1
                    f.write(f"""hide_version("{item.version.module_load}")\n""")

        logger.info("GCCcore %s: %d modules will be hidden by %s", gcc.version.version, count, filename)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Produce Lmod hide module files')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')

    args = parser.parse_args()

    set_up_logging(args.debug)
    main()
