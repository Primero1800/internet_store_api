from datetime import timedelta

from celery import Celery

from celery_home.beat_home.beat_schedule import schedule as beat_schedule
from celery_home.settings import settings

# command
#  celery -A celery_home.config.app_celery worker --loglevel=info | celery -A celery_home.config.app_celery flower | celery -A celery_home.config.app_celery beat  --loglevel=info
app_celery = Celery(settings.celery.APP_NAME)


app_celery.config_from_object("celery_home.file_config")

app_celery.conf.broker_url = settings.celery.CELERY_BROKER_URL
app_celery.conf.result_backend = settings.celery.CELERY_BROKER_BACKEND
app_celery.conf.timezone = settings.celery.APP_TIMEZONE

app_celery.conf.result_expires = timedelta(days=settings.celery.CELERY_RESULT_EXPIRES_DAYS)
# app_celery.conf.result_expires = timedelta(hours=settings.celery.CELERY_RESULT_EXPIRES_HOURS)


app_celery.autodiscover_tasks(
    packages=["src.api.v1.celery_tasks",]
)


app_celery.conf.beat_schedule = beat_schedule
