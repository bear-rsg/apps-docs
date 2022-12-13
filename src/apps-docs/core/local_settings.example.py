"""
Settings that are specific to this particular instance of the project.
This can contain sensitive information (such as keys) and should not be shared with others.

REMEMBER: If modfiying the content of this file, reflect the changes in local_settings.example.py
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create a SECRET_KEY.
# Online tools can help generate this for you, e.g. https://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = ''

# Set to True if in development, or False is in production
DEBUG = True / False

# Set to ['*'] if in development, or specific IP addresses and domains if in production
ALLOWED_HOSTS = ['*']

# Website config file
WEBSITE_SITE_CONFIG_FILE = "config.json"

# Set the database name below
DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': 'bear_apps_docs',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'TEST': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'bear_apps_docs_TEST.sqlite3'),
        },
    }
}

# If working with a different live vs test database setup then use the block below
# However, some uses of the scripts can have 'test' in sys.argv!
# if 'test' in sys.argv or 'test_coverage' in sys.argv:  # Covers regular testing and django-coverage
#     DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
#     DATABASES['default']['NAME'] = os.path.join(BASE_DIR, 'bear_apps_docs_TEST.sqlite3')
