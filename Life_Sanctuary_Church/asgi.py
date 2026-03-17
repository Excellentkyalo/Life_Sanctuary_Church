# Life_Sanctuary_Church/asgi.py
"""
ASGI config for Life_Sanctuary_Church project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Life_Sanctuary_Church.settings')

application = get_asgi_application()