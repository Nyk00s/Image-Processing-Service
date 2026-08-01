from .celery_app import celery_app
from app.transformations import DISPATCH


@celery_app.task
def transform_image(task_id: str):

    for op in operations:
        img = DISPATCH[op.type](img, op)
    