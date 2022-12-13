#!venv/bin/python
import framework  # NOQA
import logging
import sys
from packaging.version import parse as parse_version
from django.db import IntegrityError, transaction
from bear_applications.models import (Application, Version, Architecture, BearAppsVersion,
                                      ParagraphData, Link, CurrentVersion)


logger = logging.getLogger(__name__)


class DependencyNotFoundError(Exception):
    pass


def abort(msg):
    """
    Quit with this message
    """
    logger.error(msg)
    sys.exit(1)


def set_up_logging(debug):
    """
    Set up logging message format and level
    """
    fmt_prefix = "[%(levelname)s] %(message)s"
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(fmt=fmt_prefix))
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    if debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


def get_application(name, version=None):
    """
    Returns a tuple of (Application object, Version object (or None))
    """
    try:
        app = Application.objects.get(name=name)
    except Application.DoesNotExist:
        abort("Can't find application %s" % name)

    if version:
        try:
            ver = Version.objects.get(application=app, version=version)
        except Version.DoesNotExist:
            abort("Can't find %s version %s" % (name, version))
    else:
        ver = None
        version = 'All versions'

    return (app, ver)


def upload_data(name, version, arch, bav_family, module_load, home, desc, created, modified, ext=None, deps=None):
    """
    Upload this data to the database
    """
    logger.info("Uploading %s/%s", name, version)

    try:
        app = Application.objects.get(name=name)
    except Application.DoesNotExist:
        app = Application()
        app.name = name
        app.description = desc
        app.more_info = home
        app.save()
        logger.info("Created application %s", name)
    else:
        logger.info("Application %s already exists", name)

    if arch is not None:
        try:
            architecture = Architecture.objects.get(name=arch)
        except Architecture.DoesNotExist:
            architecture = Architecture()
            architecture.name = arch
            architecture.displayed_name = arch
            architecture.save()
            logger.info("Created architecture %s", arch)

    if bav_family is not None:
        try:
            bav = BearAppsVersion.objects.get(name=bav_family)
        except BearAppsVersion.DoesNotExist:
            bav = BearAppsVersion()
            bav.name = bav_family
            bav.displayed_name = bav_family
            bav.auto_loaded = False
            bav.hidden = False
            bav.deprecated = False
            bav.save()
            logger.info("Created bearappsversion family %s", bav_family)

    try:
        ver = Version.objects.get(application=app, version=version)
        new_ver = False
    except Version.DoesNotExist:
        ver = Version()
        ver.application = app
        ver.version = version
        ver.module_load = module_load
        ver.created = created
        ver.modified = modified
        ver.save()

        new_ver = True

        logger.info("Created version %s", version)

        if ext is not None:
            para = ParagraphData()
            para.header = 'Extensions'
            para.content = _parse_ext_list_to_html(ext)
            # only set one of para.version or para.application
            para.version = ver
            para.save()
            logger.info("Set extension info in a paragraph")

    else:
        logger.info("Version %s already exists", version)

    if arch is not None and bav_family is not None:
        try:
            link = Link.objects.get(version=ver, architecture=architecture, bearappsversion=bav)
        except Link.DoesNotExist:
            link = Link()
            link.version = ver
            link.architecture = architecture
            link.bearappsversion = bav
            link.save()
            logger.info("Linked %s, %s and %s", version, arch, bav_family)

    if new_ver:
        set_cv = False

        try:
            current_version = CurrentVersion.objects.get(application=app)
        except CurrentVersion.DoesNotExist:
            set_cv = True
        except CurrentVersion.MultipleObjectsReturned:
            for obj in CurrentVersion.objects.filter(application=app):
                logger.warning("Multiple objects found for current version - deleting %s", obj)
                obj.delete()
            set_cv = True
        else:
            if (current_version.version.modified < modified and
                    parse_version(current_version.version.version) < parse_version(ver.version)):
                set_cv = True
                current_version.delete()

        if set_cv:
            current_version = CurrentVersion()
            current_version.application = app
            current_version.version = ver
            current_version.save()
            logger.info("Set as current version")

    if deps:
        set_dependencies(ver, deps)


def set_dependencies(ver, deps):
    """
    Set the items in deps as dependencies for ver
    Raise an error if a dep is not in the database
    """
    try:
        with transaction.atomic():
            ver.dependencies.clear()
            for dep in deps:
                logger.debug("Checking dep %s", dep)
                dep_split = dep.split('/')
                if len(dep_split) != 2:
                    logger.warning("Discarding potential dep '%s' as it doesn't match 'a/b'", dep)
                    continue
                dep_app, dep_ver = get_application(dep_split[0], dep_split[1])
                ver.dependencies.add(dep_ver)
                logger.info("Set %s/%s as dependency", dep_app.name, dep_ver.version)
    except IntegrityError as e:
        raise DependencyNotFoundError(str(e))


def _parse_ext_list_to_html(ext_list):
    """
    Take an extension list and convert to a html list
    """
    output = ""
    for ext in ext_list.split(','):
        ext_split = ext.strip().split("-")
        if len(ext_split) == 2:
            output = "{}<li>{} {}</li>".format(output, ext_split[0], ext_split[1])
        else:
            output = "{}<li>{}</li>".format(output, ext)
    output = "<ul>{}</ul>".format(output)
    return output
