from app.models import UserModel
from sqlalchemy.orm import Session
from app.security import hash_password
from sqlalchemy.exc import IntegrityError
from app.repositories import UserRepository
from app.schemas import UserCreate, UserRead
from app.exceptions import EmailAlreadyExistsError


class UserService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository 

    def register(self, user_create: UserCreate) ->  UserRead:

        if self.user_repository.get_by_email(user_create.email):
            raise EmailAlreadyExistsError()

        hash = hash_password(user_create.password.get_secret_value())
        user = UserModel(
            email=user_create.email,
            password_hash=hash
        )
        try:
           user = self.user_repository.add_user(user)
        except IntegrityError:
            raise EmailAlreadyExistsError()
        return UserRead.model_validate(user)
        