# Import this in your script to allow it to access, e.g. the models of this django project

import os
import sys
import django

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent, 'src/apps-docs/'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
