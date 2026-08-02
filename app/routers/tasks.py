from uuid import UUID
from app.models import UserModel
from app.services import TaskService
from app.schemas import TaskList, TaskDetail
from app.exceptions import TaskNotFoundError
from fastapi import APIRouter, Query, Depends, HTTPException
from app.dependencies import get_current_user, get_task_service

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get("", response_model=TaskList, status_code=200)
def handle_get_tasks(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, le=100, ge=1),
    user: UserModel = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    return task_service.list_tasks(user, page=page, per_page=per_page)


@router.get("/{id}", response_model=TaskDetail, status_code=200)
def handle_get_single_task(
        id: UUID,
        user: UserModel = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
):
    try:
        return task_service.get_task(id, user)
    except TaskNotFoundError:
        raise HTTPException(404, "Task not found")
