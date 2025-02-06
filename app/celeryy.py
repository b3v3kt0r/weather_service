from celery import Celery


celery_app = Celery("weather_service", broker="redis://redis:6379")

celery_app.autodiscover_tasks(packages=["app.weather"])
