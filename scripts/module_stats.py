#!/usr/bin/env python

import argparse
import calendar
from datetime import datetime
import io
import logging
import os
from pathlib import Path
import pytz
import random
import re
import time

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    from wordcloud import WordCloud
except ImportError:
    raise ImportError('You need a virtualenv with matplotlib, numpy, Pillow and wordcloud installed')

# N.B. this script will fail if the local_settings.py file is missing
from functions import set_up_logging
import framework  # NOQA
from bear_applications.models import Link, Version

logger = logging.getLogger(__name__)

"""
This script gathers statistics on BlueBEAR's modules and can optionally create wordmaps and graphs to illustrate this
data.

It requires Python 3 and the following Python modules to be available:
  * matplotlib
  * numpy
  * Pillow
  * wordcloud

Please use the `requirements-module_stats.txt` file at the top of this repo to install the necessary modules:

```
pip install -r requirements-module_stats.txt
```
"""


class ModuleStats:

    def __init__(self):
        self.version_regex = re.compile(r"[v|V]?((\d+[.|-])*\d+)-?.*")
        self.timezone = pytz.timezone("Europe/London")

    def _full_list_dict(self):
        """
        Traverse the database and build a dictionary that has the module name as the key and
        a list of version objects as the value
        """

        full_list_dict = {}

        for v in Version.objects.filter(reason_to_hide=None, application__reason_to_hide=None):
            module_name = v.application.name
            if module_name in full_list_dict:
                full_list_dict[module_name].append(v)
            else:
                full_list_dict[module_name] = [v]

        return full_list_dict

    def _order_by_version(self, version_instance):
        """
        Used by the sorted function to order module version lists semantically, where possible
        """

        version_string = version_instance.version
        match = self.version_regex.match(version_string)
        if match:
            return_list = [""]
            try:
                return_list.extend([int(x) for x in match[1].replace('-', '.').split(".")])
                return tuple(return_list)
            except ValueError as e:
                logger.debug("CANNOT PARSE TO INTS! %s for %s", version_string, version_instance.application.name)
                logger.debug("\tError: %s", e)
                return tuple(version_string)
        else:
            logger.debug("NO MATCH! %s for %s", version_string, version_instance.application.name)
            return tuple(version_string)

    def _build_activity_dict(self):
        """
        Iterate over the main dictionary and build a new dict which
        collates the application versions built based on year & week
        """

        activity_dict = {}

        for v in Version.objects.filter(reason_to_hide=None, application__reason_to_hide=None):
            year, week, _ = v.modified.isocalendar()
            activity_dict.setdefault(year, {})
            activity_dict[year].setdefault(week, set()).add((v.application.name, v.version))

        return activity_dict

    def _applications_in_timeframe(self, start_date, end_date=None):
        """
        Wrapper to the raw function that converts a datestring into a date object.
        """

        if start_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_date_obj = datetime.fromtimestamp(0)

        if end_date:
            # Ensure that a date is parsed to the end of the given day
            end_date_obj = datetime.strptime(f"{end_date}_235959", "%Y-%m-%d_%H%M%S")
        else:
            end_date_obj = datetime.now()

        return self._applications_in_timeframe_raw(start_date_obj, end_date_obj)

    def _applications_in_timeframe_raw(self, start_date, end_date):
        """
        Performs a filtered database lookup and returns a Django QuerySet which only includes application versions
        built within the defined time period. Expects datetime.datetime objects.
        """

        start_date_tz = self.timezone.localize(start_date)
        end_date_tz = self.timezone.localize(end_date)

        timeframed_modules = Version.objects.filter(
            reason_to_hide=None,
            application__reason_to_hide=None,
            modified__range=[start_date_tz, end_date_tz],
        ).order_by('application__name', 'version')

        return timeframed_modules

    def _check_create_outfile(self, basedir, filename_base, extension):
        """
        Given a basepath and filename information, constructs and filepath for writing to, creating directories
        where required.
        """

        basedir = os.path.expanduser(basedir)
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        datetime_now = time.strftime("%Y_%m_%d-%H%M%S", time.localtime())
        filename = f"{filename_base}-{datetime_now}.{extension}"

        return os.path.join(basedir, filename)

    def monthly_report(self, year, month):
        """
        Extracts applications from the master dictionary depending on the year and month in which they were created.
        Builds a table from the data in markdown format and returns this as a string.
        """

        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

        monthly_app_strings = []

        # Django QuerySet of filtered modules
        monthly_apps = self._applications_in_timeframe_raw(start_date, end_date)

        for version in sorted(monthly_apps, key=self._order_by_version, reverse=False):
            monthly_app_strings.append(f"| {version.application.name} | {version.version} | {version.module_load} |")

        output_strings_list = []

        # N.B. the number of apps printed here only counts each application **name** once, i.e. it doesn't count
        # versions and/or toolchains
        output_strings_list.append(
            f"Applications added in {calendar.month_name[month]} {year}: **{len(monthly_apps)}**\n"
        )
        output_strings_list.append("| Application | Version | Load cmd |")
        output_strings_list.append("| ------ | ------- | ------- |")
        output_strings_list.extend(sorted(monthly_app_strings, key=lambda s: s.lower()))

        output_string = "\n".join(output_strings_list)

        return output_string

    def annual_activity_plot(self, year, dir):
        """
        Plot a graph that shows how many applications were built during each week of a year
        """

        output_filepath = self._check_create_outfile(dir, "annual_activity_plot", "pdf")

        activity_dict = self._build_activity_dict()
        activity_list = []

        annual_count = 0

        for x in range(52):
            x += 1
            week = activity_dict[year].get(x, [])
            week_count = len(week)
            annual_count += week_count
            activity_list.append(week_count)

        # this is for plotting purposes
        index = np.arange(len(activity_list))

        plt.bar(index, activity_list)
        plt.xlabel('Week', fontsize=5)
        plt.ylabel('Number of applications built', fontsize=8)
        plt.xticks(index, range(1, 53), fontsize=4, rotation=90)
        plt.title(f"BlueBEAR applications built during {year}, by week")
        plt.savefig(output_filepath)

        start_date = datetime(year, 1, 1, 0, 0, 0)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        yearly_app_names = []
        yearly_app_strings = []
        yearly_apps = self._applications_in_timeframe_raw(start_date, end_date)

        for version in yearly_apps:
            module_name = version.application.name
            yearly_app_strings.append(
                f"| {module_name} ({version.modified}) | {version.version} | {version.module_load} |"
            )
            if module_name not in yearly_app_names:
                yearly_app_names.append(module_name)

        output_strings_list = []

        # N.B. the number of apps printed here only counts each application **name** once, i.e. it doesn't count
        # versions and/or toolchains
        output_strings_list.append(f"Modules added in {year}: **{len(yearly_apps)}**")
        output_strings_list.append(f"Applications (by name) added in {year}: **{len(yearly_app_names)}**\n")
        output_strings_list.append("| Application | Version | Load cmd |")
        output_strings_list.append("| ------ | ------- | ------- |")
        output_strings_list.extend(sorted(yearly_app_strings, key=lambda s: s.lower()))

        output_string = "\n".join(output_strings_list)

        return output_string

    def build_wordcloud(self, mask_file, dir, start_date=None, end_date=None, exclude_list=[]):
        """
        Creates a dictionary that has the application name as the key and the number of versions
        available on BlueBEAR as the value.
        Builds an image within the shape of the mask provided and colour the text in various shades of blue.
        """

        output_filepath = self._check_create_outfile(dir, "apps_wordcloud", "png")

        modules_to_exclude = ['python2', 'python3', 'python']
        modules_to_exclude.extend([x.lower() for x in exclude_list])

        if not start_date and not end_date:
            input_data = Version.objects.filter(reason_to_hide=None, application__reason_to_hide=None)
        else:
            input_data = self._applications_in_timeframe(start_date, end_date)

        # Builds a dictionary with the app name as the key and the counter (i.e. number of versions
        # available on BlueBEAR) as the value.
        wordcloud_dict = {}
        for v in input_data:
            module_name = v.application.name
            if module_name.lower() in modules_to_exclude:
                continue
            elif module_name in wordcloud_dict:
                wordcloud_dict[module_name] += 1
            else:
                wordcloud_dict[module_name] = 1

        # See https://hslpicker.com - the first number provides the colour hue
        def colour_function(word, font_size, position, orientation, random_state=None,
                            **kwargs):
            return "hsl(%d, %d%%, %d%%)" % (random.randint(10, 30), random.randint(20, 100), random.randint(30, 70))

        with open(mask_file, 'rb') as f:
            bear_mask = np.array(Image.open(io.BytesIO(f.read())))

        wc = WordCloud(background_color="white", max_words=2000, mask=bear_mask,
                       contour_width=0.5, contour_color='black')

        # generate word cloud
        wc.generate_from_frequencies(wordcloud_dict)
        wc.recolor(color_func=colour_function, random_state=3)

        # store to file
        wc.to_file(output_filepath)

    def full_listing(self):
        """
        List every application found alongside its available versions
        """

        full_list = self._full_list_dict()

        output_list = []

        apps_counter = 0
        module_versions_counter = 0

        for mod_name, versions_list in sorted(full_list.items(), key=lambda x: x[0].lower()):
            temp_list = []
            display_name = mod_name
            apps_counter += 1

            for version in sorted(versions_list, key=self._order_by_version, reverse=False):
                module_versions_counter += 1
                arch_str = ", ".join(
                    [f"{t.architecture.name} ({t.bearappsversion.displayed_name})"
                     for t in Link.objects.filter(version=version).exclude(bearappsversion__hidden=1)]
                )
                temp_list.append(
                    f"\t{version.module_load} (built: {version.modified.strftime('%c')}). Architecture: {arch_str}"
                )
            output_list.append(display_name)
            output_list.extend(temp_list)

        output_list.append('\n\n')
        output_list.append(f'Total applications installed: {apps_counter}\n')
        output_list.append(f'Total module versions installed: {module_versions_counter}\n')

        output_string = "\n".join(output_list)
        return output_string


def main():

    parser = argparse.ArgumentParser(description="Generate statistics and infomatics for BEAR Applications")
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debugging output')

    # Define top level arguments
    subparsers = parser.add_subparsers(help='Please choose in which mode you want to run the script:',
                                       dest='usage_mode',
                                       )

    # Arguments for annual plot
    parser_annual_plot = subparsers.add_parser('annual-plot',
                                               help=("Generate a graph showing the number applications built "
                                                     "across each week of a given year")
                                               )
    parser_annual_plot.add_argument('year', type=int)
    parser_annual_plot.add_argument('-o', '--output', dest='output_dir',
                                    required=True,
                                    help=("Choose a directory for writing output files. "
                                          "Will be created if doesn't alrady exist."),
                                    )

    # Arguments for full listing
    subparsers.add_parser('full-list', help="List all of the applications and vesions installed")

    # Arguments for monthly stats
    parser_monthly = subparsers.add_parser('monthly',
                                           help="List all modules built in a given year and month")
    parser_monthly.add_argument('year', type=int)
    parser_monthly.add_argument('month', type=int)

    # Arguments for wordcloud
    parser_wordcloud = subparsers.add_parser('wordcloud',
                                             help=("Generate a wordcloud based on the number of versions of an "
                                                   "application (optionally within a specified timeframe)")
                                             )
    parser_wordcloud.add_argument('--maskfile', default=Path(__file__).parent / 'wordcloud_bear.png',
                                  help="Select a png image file to use as a shape mask for the worcloud")
    parser_wordcloud.add_argument('--start',
                                  help="Start date, provided in the following format: YYYY-MM-DD, e.g. 2019-01-01")
    parser_wordcloud.add_argument('--end',
                                  help="End date, provided in the following format: YYYY-MM-DD, e.g. 2019-01-01")
    parser_wordcloud.add_argument('-o', '--output', dest='output_dir',
                                  required=True,
                                  help=("Choose a directory for writing output files. "
                                        "Will be created if it doesn't already exist."),
                                  )
    parser_wordcloud.add_argument('--exclude', action='append', required=False,
                                  default=[],
                                  help=("Specify additional modules to exclude."),
                                  )

    args = parser.parse_args()

    set_up_logging(args.debug)

    if not args.usage_mode:
        logger.error("Please choose a mode in which you want to run the script")
        raise SystemExit(1)

    mod_stats = ModuleStats()

    if args.usage_mode == 'annual-plot':
        annual_markdown = mod_stats.annual_activity_plot(args.year, args.output_dir)
        logger.info(annual_markdown)
    elif args.usage_mode == 'full-list':
        logger.info(mod_stats.full_listing())
    elif args.usage_mode == 'monthly':
        logger.info(mod_stats.monthly_report(args.year, args.month))
    elif args.usage_mode == 'wordcloud':
        mod_stats.build_wordcloud(args.maskfile, args.output_dir, start_date=args.start,
                                  end_date=args.end, exclude_list=args.exclude)


if __name__ == '__main__':
    main()
