from app.models import UserModel
from app.schemas import PictureRead
from app.services import PictureService
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from app.exceptions import InvalidImageError, MaxUploadSizeExceededError
from app.dependencies import get_current_user, get_picture_service

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