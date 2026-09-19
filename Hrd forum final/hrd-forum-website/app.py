"""
app.py - Legacy Flask Entry Point (Unified on Django)

The application has been unified under Django (hrd_project).
This file delegates to Django's WSGI application for compatibility.
"""
import os
import sys

# Ensure Django settings module is configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrd_project.settings')

from hrd_project.wsgi import application as app

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    print("Starting HRD Forum Django Server...")
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])