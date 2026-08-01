from celery import Celery
from app.config import Config

settings = Config()

celery_app = Celery("celery_app", broker=settings.redis_broker_url)
