from pydantic import BaseModel, EmailStr

class RoleCreate(BaseModel):
    name: str
    description: str = ""

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    role_id: int
    first_name: str = ""
    last_name: str = ""

class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None
    role_id: int = None
