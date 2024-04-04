import os

from celery import Celery

# Задать модуль настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myShop.settings")

app = Celery("myshop")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
