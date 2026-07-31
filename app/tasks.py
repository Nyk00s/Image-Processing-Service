from app.celery_app import celery_app


@celery_app.task
def transform_image(task_id: str):
    pass