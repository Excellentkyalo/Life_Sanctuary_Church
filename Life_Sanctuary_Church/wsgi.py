# Life_Sanctuary_Church/wsgi.py
"""
WSGI config for Life_Sanctuary_Church project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Life_Sanctuary_Church.settings')

application = get_wsgi_application()