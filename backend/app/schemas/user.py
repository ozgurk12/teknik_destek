from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re

from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.KULLANICI

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError('Username can only contain letters, numbers, underscore and hyphen')
        return v

class UserCreateByAdmin(UserCreate):
    role: UserRole
    module_ids: List[UUID] = []

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

class UserUpdateByAdmin(UserUpdate):
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    module_ids: Optional[List[str]] = None  # UUID as string for better compatibility

class ModuleBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None

class ModuleCreate(ModuleBase):
    is_active: bool = True

class ModuleResponse(ModuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    modules: List[ModuleResponse] = []

class UserInDB(UserResponse):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserModuleAssignment(BaseModel):
    user_id: UUID
    module_ids: List[UUID]