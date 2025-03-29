from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sports_news.settings')

app = Celery('sports_news')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()