from app.models import UserModel
from sqlalchemy.exc import IntegrityError
from app.repositories import UserRepository
from app.security import hash_password, verify_password
from app.schemas import UserCreate, UserRead, UserLogin
from app.exceptions import EmailAlreadyExistsError, InvalidCredentialsError


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

    def authenticate(self, user_login: UserLogin) -> UserModel:
        if not (user := self.user_repository.get_by_email(user_login.email)):
            raise InvalidCredentialsError()
        if not verify_password(user_login.password.get_secret_value(), user.password_hash):
            raise InvalidCredentialsError()
        return user
 