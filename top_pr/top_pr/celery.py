import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'top_pr.settings')

app = Celery('top_pr')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(f'django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'order-create-10-sec': {
        'task': 'my_site.tasks.create_task_in_provider',
        'schedule': 10,
    },
    'order-status-20-sec':{
        'task': 'my_site.tasks.update_status_orders',
        'schedule': 15,
    }
}