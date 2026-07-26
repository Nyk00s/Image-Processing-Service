from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserRead, UserCreate
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import UserService
from app.repositories import UserRepository
from app.exceptions import EmailAlreadyExistsError

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

@router.post("/register", response_model=UserRead, status_code=201)
def handle_register(data: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        return service.register(data)
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already registered")
