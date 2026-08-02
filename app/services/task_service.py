from uuid import UUID
from app.storage import StorageClient
from app.worker import transform_image
from app.models import TaskModel, TaskStatus, UserModel
from app.repositories import TaskRepository, PictureRepository
from app.exceptions import PictureNotFoundError, TaskNotFoundError
from app.schemas import TaskAccepted, Operation, TaskDetail, TaskList


class TaskService:

    def __init__(self, task_repo: TaskRepository, picture_repo: PictureRepository, storage: StorageClient):
        self.task_repo = task_repo
        self.picture_repo = picture_repo
        self.storage = storage

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

    def get_task(self, id: UUID, user: UserModel) -> TaskDetail:
        if not (task := self.task_repo.get_by_id_and_user(id, user.id)):
            raise TaskNotFoundError()
        key = task.result_storage_key
        url = self.storage.generate_presigned_url(key) if key else None
        return TaskDetail(
            id=task.id, picture_id=task.picture_id, operations=task.operations,
            status=task.status, error_message=task.error_message, created_at=task.created_at,
            finished_at=task.finished_at, url=url
        )

    def list_tasks(self, user: UserModel, page: int, per_page: int) -> TaskList:
        tasks = self.task_repo.list_by_user(user.id, per_page, (page - 1) * per_page)
        count_of_tasks = self.task_repo.count_by_user(user.id)
        return TaskList(
            tasks=tasks,
            per_page=per_page,
            page=page,
            total=count_of_tasks
        )
