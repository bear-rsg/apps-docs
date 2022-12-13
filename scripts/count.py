#!venv/bin/python
import logging
from functions import set_up_logging
from bear_applications.models import CurrentVersion, Link, Version

logger = logging.getLogger(__name__)


def counts():
    """
    Counts of applications, versions, and links
    """
    application_count = CurrentVersion.objects.filter(
        version__reason_to_hide=None, version__application__reason_to_hide=None
    ).count()
    version_count = Version.objects.filter(reason_to_hide=None, application__reason_to_hide=None).count()
    link_count = Link.objects.filter(
        version__reason_to_hide=None,
        version__application__reason_to_hide=None,
        bearappsversion__hidden=False,
        architecture__hidden=False,
    ).count()

    logger.info("All counts are for unhidden items")
    logger.info("Application count: %s", application_count)
    logger.info("Version count: %s", version_count)
    logger.info("Combo count: %s", link_count)


if __name__ == "__main__":
    set_up_logging(False)

    counts()
