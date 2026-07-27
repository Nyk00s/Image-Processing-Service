from pydantic import BaseModel, SecretStr, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr
