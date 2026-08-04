from app.models import UserModel
from app.services import UserService
from fastapi import APIRouter, Depends 
from app.repositories import UserRepository
from app.tokens import create_refresh_token, create_access_token
from app.schemas import UserRead, UserCreate, UserLogin, TokensSchema, RefreshRequest
from app.dependencies import get_user_service, get_current_user, get_user_repository, resolve_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def handle_register(data: UserCreate, service: UserService = Depends(get_user_service)):
    return service.register(data)


@router.post("/login", response_model=TokensSchema, status_code=200)
def handle_login(data: UserLogin, service: UserService = Depends(get_user_service)):
    user = service.authenticate(data)
    return TokensSchema(
        access_token=create_access_token(user.id, user.token_version),
        refresh_token=create_refresh_token(user.id, user.token_version)
    )


@router.get("/me", response_model=UserRead)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=TokensSchema, status_code=200)
def handle_refresh(
    refresh_token: RefreshRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    user = resolve_refresh_token(refresh_token.refresh_token, user_repo)
    return TokensSchema(
            access_token=create_access_token(user.id, user.token_version),
            refresh_token=create_refresh_token(user.id, user.token_version)
    ) 


@router.post("/logout", status_code=204)
def handle_logout(
    current_user: UserModel = Depends(get_current_user), 
    user_repo: UserRepository = Depends(get_user_repository)
):
    user_repo.increment_token_version(current_user)
