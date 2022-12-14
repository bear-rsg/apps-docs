# Apps Docs

Used on:

* [BEAR Apps](https://bear-apps.bham.ac.uk/)
* [Baskerville Apps](https://apps.baskerville.ac.uk/)


## Setup

1. `pip install .` in the base directory
   * MySQL / MariaDB: `pip install .[mysql]`
   * PostgreSQL: `pip install .[postgres]`
   * Testing / development: `pip install .[testing,linting]`
1. `cd src/apps-docs`
1. Prepare equivalents of
   * `core/templates/base_bear.html`
   * `bear_applications/templates/bear_applications/help_bear.html`
   * `bear_applications/templates/bear_applications/home_bear.html`
1. `cp core/bear.json core/my_config.json`
   * Name this file for your system
   * Edit this file as required, linking in the pages created in the previous section
1. `cp core/local_settings.example.py core/local_settings.py`
   * Edit this file as required
1. `python manage.py migrate`
1. Set up production hosting, for example using nginx and uwsgi (see <https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/uwsgi/>)


## Scripts and Adding and Editing Data

All data is added, or edited, via the scripts in the `scripts` directory.

### `add_module_info.sh` and `add_module_info.py`

These are used to parse a module file and add it to the database. This parses Tcl module files
generated by EasyBuild.


## BEAR Module Setup

These are several references to BEAR Apps Versions in the code. BlueBEAR and Baskerville are
setup so that a subset of modules are installed together, in a groups ('BEAR App Version') and
these groupings require a `module load` command to access (which may be enabled by default of
not).

Beyond these we operate a flat module naming scheme.
