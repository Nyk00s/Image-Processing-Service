from uuid import UUID
from app.worker import transform_image
from app.models import TaskModel, TaskStatus
from app.schemas import TaskAccepted, Operation
from app.repositories import TaskRepository, PictureRepository
from app.exceptions import PictureNotFoundError


class TaskService:

    def __init__(self, task_repo: TaskRepository, picture_repo: PictureRepository):
        self.task_repo = task_repo
        self.picture_repo = picture_repo

    def create_transformation(
            self, 
            picture_id: UUID, 
            user_id: UUID, 
            operations: list[Operation]
    ) -> TaskAccepted:
        if not self.picture_repo.get_by_id_and_user(picture_id, user_id):
            raise PictureNotFoundError()

        task = TaskModel(
            picture_id=picture_id,
            operations=[op.model_dump() for op in operations],
            status=TaskStatus.PENDING
        )
        task = self.task_repo.add(task)
        transform_image.delay(str(task.id))
        return TaskAccepted(
            task_id=task.id,
            status=task.status
        )
