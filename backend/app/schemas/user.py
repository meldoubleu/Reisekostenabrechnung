from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    employee = "employee"
    controller = "controller"
    admin = "admin"


class UserBase(BaseModel):
    email: str = Field(..., example="max.mustermann@demo.com")
    name: str = Field(..., example="Max Mustermann")
    role: UserRole
    company: str = Field(..., example="Demo GmbH")
    department: Optional[str] = Field(None, example="Sales")
    cost_center: Optional[str] = Field(None, example="SALES-001")
    is_active: bool = True


class UserCreate(UserBase):
    controller_id: Optional[int] = None
    password: Optional[str] = None
    password_hash: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    company: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    is_active: Optional[bool] = None
    controller_id: Optional[int] = None


class User(UserBase):
    id: int
    controller_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserWithRelations(User):
    controller: Optional[User] = None
    employees: List[User] = Field(default_factory=list)

    class Config:
        from_attributes = True
