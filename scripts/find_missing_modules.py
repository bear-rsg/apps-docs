#!venv/bin/python
import os
import logging
import tqdm
from functions import set_up_logging
from bear_applications.models import Link

logger = logging.getLogger(__name__)


BASE = "/rds/bear-apps/"
MIN_BAV = "2018b"  # sorted alphabetically


def find_missing_modules(bear_apps_version=None):
    """
    Find modules in the database that don't exist on disk - and optionally delete them
    """
    if bear_apps_version:
        links = Link.objects.filter(bearappsversion__name=bear_apps_version)
    else:
        links = Link.objects.all()

    missing = []
    skipped = 0
    with tqdm.tqdm(list(links), desc="Finding missing modules") as tq:
        for link in tq:
            tq.set_postfix({'missing': len(missing), 'skipped': skipped})
            tq.refresh()
            bav = link.bearappsversion.name
            if bav < MIN_BAV:
                if not skipped:
                    logger.warning("I skip anything earlier than bear-apps/%s - things were different then", MIN_BAV)
                skipped += 1
                continue
            if bav.endswith('h'):
                # handbuilt - the path may be different
                skipped += 1
                continue

            app = link.version.application.name
            if app.startswith('OpenFOAM '):  # including the final space
                app = 'OpenFOAM'
            elif ' ' in app:
                logger.warning("App name '%s' with a space is unlikely to be the name on disk - skipping", app)
                skipped += 1
                continue

            ver = link.version.version
            arch = link.architecture.name
            target = os.path.join(BASE, bav, arch, 'modules/all', app, ver)
            if os.path.exists(target):
                continue
            else:
                missing.append((link, target))

    logger.info("Found %d missing modules", len(missing))
    for link, target in missing:
        logger.info("Could not find %s on disk", target)

    if missing:
        delete = (input("\nDelete them? [y/N]").lower().strip() == 'y')
    if delete:
        for link, target in missing:
            link.delete()
            logger.warning("Deleted %s from the database", target)
    else:
        logger.warning("Aborting")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=("Find modules in the database that don't exist on disk - and "
                                                  "optionally delete them"))
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('-b', '--bear-apps-version', help='BEAR apps version, e.g. 2018b. Default is to do all.')

    args = parser.parse_args()
    set_up_logging(args.debug)
    find_missing_modules(args.bear_apps_version)
