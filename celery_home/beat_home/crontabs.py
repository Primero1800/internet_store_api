from celery.schedules import crontab


class Crontabs:
    every_minute: crontab = crontab(minute='*')                     # Запуск каждую минуту
    every_2_minutes: crontab = crontab(minute='*/2')           # Запуск каждые 2 минуты
    every_10_minutes: crontab = crontab(minute='*/10')       # Запуск каждые 10 минут
    every_day: crontab = crontab(minute='0', hour='0')      # Запуск каждый день в 00:00
    every_hour: crontab = crontab(minute='0')                         # Запуск каждый час
