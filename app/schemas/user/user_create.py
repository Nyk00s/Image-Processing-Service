from pydantic import BaseModel, EmailStr, SecretStr


class UserCreate(BaseModel):
    password: SecretStr
    email: EmailStr
