from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False, nullable=False)  # Nuevo campo
    is_staff = Column(Boolean, default=False, nullable=False)      # Nuevo campo

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    date_joined = Column(DateTime, default=datetime.now, nullable=False)
    last_login = Column(DateTime, nullable=True)

    role = relationship("Role", back_populates="users")
