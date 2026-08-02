import io
import uuid
import logging
from PIL import Image
from app.config import Config
from pydantic import TypeAdapter
from app.schemas import Operation
from app.models import TaskStatus
from .celery_app import celery_app
from app.database import SessionLocal
from datetime import datetime, timezone
from app.storage import get_storage_client
from app.repositories import TaskRepository, PictureRepository
from app.transformations import DISPATCH

operations_adapter = TypeAdapter(list[Operation])
settings = Config()
storage = get_storage_client(settings)

def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


@celery_app.task
def transform_image(task_id: str) -> None:

    db = SessionLocal()
    try:

        task_repo = TaskRepository(db)
        picture_repo = PictureRepository(db)

        task = task_repo.get_by_id(uuid.UUID(task_id))
        if task is None:
            logging.error(f"Task id: {task_id} does not exist")
            return
        task.status = TaskStatus.PROCESSING
        task = task_repo.update(task)
        operations = operations_adapter.validate_python(task.operations)

        picture = picture_repo.get_by_id(task.picture_id)

        if picture is None:
            msg = f"Picture id: {task.picture_id} does not exist"
            task.finished_at = get_current_time()
            task.error_message = msg
            task.status = TaskStatus.FAILED
            task_repo.update(task)
            logging.error(msg)
            return 

        picture_bytes = storage.download(picture.storage_key)
        if not picture:
            msg = "Picture is empty"
            task.finished_at = get_current_time
            task.error_message = msg
            task.status = TaskStatus.FAILED
            task_repo.update(task)
            logging.error(msg)
            return
        try:
            img = Image.open(io.BytesIO(picture_bytes))
            original_format = img.format # If format operations, won't work TODO: change that
            for op in operations:
                img = DISPATCH[op.type](img, op)
            if original_format in ("JPEG", "JPG") and img.mode != "RGB":
                img = img.convert("RGB")

            out = io.BytesIO()
            img.save(out, format=original_format)
            result_key = f"users/{picture.user_id}/derived/{task.picture_id}/{task.id}.{original_format.lower()}"
            storage.upload(result_key, out.getvalue(), Image.MIME.get(original_format))
            task.status = TaskStatus.COMPLETED
            task.result_storage_key = result_key
            task.finished_at = get_current_time()
        except Exception as e:
            msg = str(e)
            task.error_message = msg
            task.status = TaskStatus.FAILED
            task.finished_at = get_current_time()
            logging.error(msg)
        task_repo.update(task)
    finally:
        db.close()
    