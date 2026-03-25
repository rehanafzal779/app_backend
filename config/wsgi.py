import os
from django.core.wsgi import get_wsgi_application

# Use production settings if DJANGO_SETTINGS_MODULE is not set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development'))

application = get_wsgi_application()