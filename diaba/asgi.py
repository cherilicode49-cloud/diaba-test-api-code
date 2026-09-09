import os
import django
import socketio

from django.core.asgi import get_asgi_application

#  IMPORTANT: set settings BEFORE django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diaba.settings")

# Setup Django
django.setup()

#  Import AFTER django.setup()
from diabaApp.consumers.consumer import sio


# Create Django ASGI app
django_app = get_asgi_application()


# Combine Socket.IO + Django
application = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=django_app,
)
