#!venv/bin/python
from functions import set_up_logging
from bear_applications.models import Application, Version


def delete(*, delete, doit=False):
    """ Delete all items """

    if not doit:
        print("Dry run, so not really deleting anything")

    if delete == 'apps':
        apps = Application.objects.filter(reason_to_hide__isnull=False)
        for app in apps:
            print(f"* Deleting application: {app.name}")
            if doit:
                app.delete()
    elif delete == 'versions':
        versions = Version.objects.filter(reason_to_hide__isnull=False)
        for ver in versions:
            print(f"* Deleting version: {ver.application.name} {ver.version}")
            if doit:
                ver.delete()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Delete hidden versions or applications.')
    parser.add_argument('delete', help='Delete apps or versions', choices=['apps', 'versions'])
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')
    parser.add_argument('--doit', help='Really delete', action='store_true')

    args = parser.parse_args()

    set_up_logging(args.debug)

    delete(delete=args.delete, doit=args.doit)
