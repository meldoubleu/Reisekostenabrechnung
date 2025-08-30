from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, ForeignKey, Text, Boolean
from ..db.session import Base
import enum
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .travel import Travel


class UserRole(str, enum.Enum):
    employee = "employee"
    controller = "controller"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    company: Mapped[str] = mapped_column(String(255))
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # For employees: who is their controller
    controller_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Relationships
    controller: Mapped[Optional["User"]] = relationship("User", remote_side=[id], back_populates="employees")
    employees: Mapped[List["User"]] = relationship("User", back_populates="controller")
    
    # Travel relationships
    travels: Mapped[List["Travel"]] = relationship("Travel", back_populates="employee")
