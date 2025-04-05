from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import multiprocessing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings')
app = Celery('project_root')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
multiprocessing.set_start_method('spawn', force=True)