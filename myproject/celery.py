from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 配置OpenTelemetry
try:
    from .opentelemetry_config import configure_opentelemetry
    configure_opentelemetry()
except Exception as e:
    print(f"Failed to configure OpenTelemetry: {e}")

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery(
    'myproject',
    broker=os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()