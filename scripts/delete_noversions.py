#!venv/bin/python
from functions import set_up_logging
from django.db.models import Count
from bear_applications.models import Application


def delete(*, doit=False):
    """ Delete all applications with no versions """

    if not doit:
        print("Dry run, so not really deleting anything")

    apps = Application.objects.annotate(ver_count=Count('version')).filter(ver_count=0)
    for app in apps:
        print(f"Delete {app.name}")
        if doit:
            app.delete()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Delete applications with no versions')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('--doit', help='Really delete', action='store_true')

    args = parser.parse_args()

    set_up_logging(args.debug)

    delete(doit=args.doit)
