import io
import uuid
import logging
from PIL import Image
from sqlalchemy import func
from app.config import Config
from pydantic import TypeAdapter
from app.schemas import Operation
from .celery_app import celery_app
from app.database import SessionLocal
from app.transformations import DISPATCH
from app.storage import get_storage_client
from app.models import TaskStatus, TaskModel
from app.repositories import TaskRepository, PictureRepository

operations_adapter = TypeAdapter(list[Operation])
settings = Config()
storage = get_storage_client(settings)


def _fail(task_repo: TaskRepository, task: TaskModel, msg: str) -> None:
    task.finished_at = func.now()
    task.error_message = msg
    task.status = TaskStatus.FAILED
    task_repo.update(task)
    logging.error(msg)


def process_image(data: bytes, operations: list[Operation]) -> tuple[bytes, str]:
    img = Image.open(io.BytesIO(data))
    output_format = img.format
    for op in operations:
        if op.type == "format":
            output_format = op.target.upper()
        else:
            img = DISPATCH[op.type](img, op)
    if output_format in ("JPEG", "JPG") and img.mode != "RGB":
        img = img.convert("RGB")
    out = io.BytesIO()
    img.save(out, format=output_format)
    return out.getvalue(), output_format


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
        picture = picture_repo.get_by_id(task.picture_id)
        if picture is None:
            _fail(task_repo, task, f"Picture id: {task.picture_id} does not exist")
            return 
        
        try:
            picture_bytes = storage.download(picture.storage_key)
            operations = operations_adapter.validate_python(task.operations)
            data, fmt = process_image(picture_bytes, operations)
            
            result_key = f"users/{picture.user_id}/derived/{task.picture_id}/{task.id}.{fmt.lower()}"
            storage.upload(result_key, data, Image.MIME.get(fmt))
            
            task.status = TaskStatus.COMPLETED
            task.result_storage_key = result_key
            task.finished_at = func.now()
            task_repo.update(task)
        except Exception as e:
            _fail(task_repo, task, str(e))
    finally:
        db.close()
    