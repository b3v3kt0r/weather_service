from celery import Celery

from app.weather.tasks import get_weather


celery_app = Celery(
    "weather_service", broker="redis://redis:6379", backend="redis://redis:6379"
)

celery_app.autodiscover_tasks(packages=["app.weather"])
