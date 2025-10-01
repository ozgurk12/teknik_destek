from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base_class import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    YONETICI = "yonetici"
    KULLANICI = "kullanici"

user_modules = Table(
    'user_modules',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('module_id', UUID(as_uuid=True), ForeignKey('modules.id', ondelete="CASCADE"), primary_key=True),
    Column('granted_by', UUID(as_uuid=True), ForeignKey('users.id'), nullable=False),
    Column('granted_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.KULLANICI)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    created_by = relationship("User", remote_side=[id], backref="created_users", foreign_keys=[created_by_id])
    modules = relationship(
        "Module",
        secondary=user_modules,
        back_populates="users",
        primaryjoin="User.id==user_modules.c.user_id",
        secondaryjoin="Module.id==user_modules.c.module_id"
    )

    def has_module_access(self, module_name: str) -> bool:
        """Check if user has access to a specific module"""
        if self.role == UserRole.ADMIN:
            return True
        return any(module.name == module_name for module in self.modules)

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"

class Module(Base):
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    users = relationship(
        "User",
        secondary=user_modules,
        back_populates="modules",
        primaryjoin="Module.id==user_modules.c.module_id",
        secondaryjoin="User.id==user_modules.c.user_id"
    )

    def __repr__(self):
        return f"<Module {self.name}>"