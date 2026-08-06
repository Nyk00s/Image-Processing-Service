from uuid import UUID
from app.models import UserModel
from app.services import PictureService, TaskService
from fastapi import APIRouter, Depends, UploadFile, Query
from app.dependencies import get_current_user, get_picture_service, get_task_service, check_upload_rate_limit
from app.schemas import PictureRead, PictureDetail, PictureList, TaskCreate, TaskAccepted

router = APIRouter(prefix="/pictures", tags=["pictures"])


@router.post("", response_model=PictureRead, status_code=201, dependencies=[Depends(check_upload_rate_limit)])
async def upload_picture( 
    file: UploadFile,
    picture_service: PictureService = Depends(get_picture_service),
    current_user: UserModel = Depends(get_current_user),
):
    picture = await picture_service.upload(file, current_user)
    return picture


@router.get("/{id}", response_model=PictureDetail, status_code=200)
def handle_get_picture(
    id: UUID, 
    user: UserModel = Depends(get_current_user),
    picture_service: PictureService = Depends(get_picture_service)
):
    return picture_service.get_picture(id, user)


@router.get("", response_model=PictureList, status_code=200)
def handle_list_pictures(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: UserModel = Depends(get_current_user),
    picture_service: PictureService = Depends(get_picture_service)
):
    return picture_service.list_pictures(user, page, per_page)


@router.post("/{id}/tasks", response_model=TaskAccepted, status_code=202)
def handle_task_creation(
    data: TaskCreate,
    id: UUID,
    user: UserModel = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    return task_service.create_transformation(id, user.id, data.operations)
