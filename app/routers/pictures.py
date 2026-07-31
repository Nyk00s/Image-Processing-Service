from uuid import UUID
from app.models import UserModel
from app.services import PictureService, TaskService
from fastapi import APIRouter, Depends, UploadFile, HTTPException, Query
from app.dependencies import get_current_user, get_picture_service, get_task_service
from app.schemas import PictureRead, PictureDetail, PictureList, TaskCreate, TaskAccepted
from app.exceptions import InvalidImageError, MaxUploadSizeExceededError, PictureNotFoundError

router = APIRouter(prefix="/pictures", tags=["pictures"])


@router.post("", response_model=PictureRead, status_code=201)
async def upload_picture( 
    file: UploadFile,
    picture_service: PictureService = Depends(get_picture_service),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        picture = await picture_service.upload(file, current_user)
    except MaxUploadSizeExceededError:
        raise HTTPException(413, "Image exceeds allowed size")
    except InvalidImageError:
        raise HTTPException(400, "Invalid image")
    return picture


@router.get("/{id}", response_model=PictureDetail, status_code=200)
def handle_get_picture(
    id: UUID, 
    user: UserModel = Depends(get_current_user),
    picture_service: PictureService = Depends(get_picture_service)
):
    try:
        return picture_service.get_picture(id, user)
    except PictureNotFoundError:
        raise HTTPException(404, "Picture not found")


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
    try:
        task = task_service.create_transformation(id, user.id, data.operations)
    except PictureNotFoundError:
        raise HTTPException(404, "Image id does not exists")
    return task
    
