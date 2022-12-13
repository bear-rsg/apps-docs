#!venv/bin/python
import logging
from functions import abort, set_up_logging
from bear_applications.models import Architecture, Gpu

logger = logging.getLogger(__name__)


def set_visibility(*, arch, hidden):
    """
    Set architecture visiblility
    """
    arch.hidden = hidden
    arch.save()
    logger.info("Architecture %s marked as %s", arch.displayed_name, 'hidden' if hidden else 'visible')


def change_displayname(*, arch, name):
    """
    Change display name
    """
    oldname = arch.displayed_name
    arch.displayed_name = name
    arch.save()
    logger.info("Architecture %s display name changed from %s to %s", arch.name, oldname, name)


def add_gpu(*, arch, gpuname):
    """
    Add GPU
    """
    Gpu.objects.create(architecture=arch, name=gpuname)
    logger.info("Added GPU %s to architecture %s", gpuname, arch.name)


def list_archs(args):
    """
    List existing architectures
    """
    for arch in Architecture.objects.all().order_by('name'):
        print("{} : {} : {}".format(arch.name, arch.displayed_name, 'Hidden' if arch.hidden else 'Visible'))
        for gpu in arch.gpu_set.all():
            print(f" * {gpu.name}")


def modify_arch(args):
    """
    Modify an architecture
    """
    try:
        arch = Architecture.objects.get(name=args.architecture)
    except Architecture.DoesNotExist:
        abort("Can't find architecture %s" % args.architecture)

    if args.hidden:
        set_visibility(arch=arch, hidden=True)
    elif args.visible:
        set_visibility(arch=arch, hidden=False)

    if args.changename:
        change_displayname(arch=arch, name=args.changename)

    if args.addgpu:
        add_gpu(arch=arch, gpuname=args.addgpu)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Modify an Architecture')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list = subparsers.add_parser('list', help='List architectures')
    parser_list.set_defaults(func=list_archs)

    parser_modify = subparsers.add_parser('modify', help='Modify an architecture')
    parser_modify.set_defaults(func=modify_arch)
    parser_modify.add_argument('architecture', help='architecture')
    parser_modify.add_argument('--hidden', action='store_true', help='Mark as hidden')
    parser_modify.add_argument('--visible', action='store_true', help='Mark as visible')
    parser_modify.add_argument('--changename', help='Change display name')
    parser_modify.add_argument('--addgpu', help='Add GPU')

    args = parser.parse_args()
    set_up_logging(args.debug)
    args.func(args)
