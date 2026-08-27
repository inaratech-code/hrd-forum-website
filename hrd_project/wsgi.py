import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrd_project.settings')

application = get_wsgi_application()

# Alias app for Vercel WSGI runner
app = application
