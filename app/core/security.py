from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str
    role: str | None = None


class UserUpdate(BaseModel):
    bio: str | None = None
    email: EmailStr | None = None


class UserRead(UserBase):
    id: int
    role: str
    bio: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
