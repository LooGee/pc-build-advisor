from celery import Celery
from celery.schedules import crontab
import os

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/2")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/3")

celery_app = Celery("pc_advisor_crawler", broker=BROKER_URL, backend=RESULT_BACKEND)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "update-prices-every-6h": {
        "task": "app.tasks.price_tasks.update_all_prices",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "discover-new-components-every-24h": {
        "task": "app.tasks.discovery_tasks.discover_new_components",
        "schedule": crontab(minute=0, hour=2),
    },
    "validate-links-every-12h": {
        "task": "app.tasks.link_validation_tasks.validate_all_links",
        "schedule": crontab(minute=30, hour="*/12"),
    },
    "cleanup-old-data-weekly": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_price_history",
        "schedule": crontab(minute=0, hour=3, day_of_week=0),
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
