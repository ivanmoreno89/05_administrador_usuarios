from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, engine
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr
import models
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SECRET_KEY = "SECRET_KEY"  # Llave secreta para JWT
ALGORITHM = "HS256"

# Crear las tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=engine)

# Instancia de FastAPI
app = FastAPI(title="Backend API", description="API para Roles, Usuarios y Autenticación", version="1.0")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints para Roles
@app.get("/roles/", tags=["Roles"])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all()
    return roles

@app.post("/roles/", tags=["Roles"])
def create_role(
    name: str,
    description: str = "",
    is_superuser: bool = False,  # Nuevo parámetro, por defecto False
    is_staff: bool = False,      # Nuevo parámetro, por defecto False
    db: Session = Depends(get_db)
):
    try:
        # Crear el rol con los valores proporcionados
        new_role = models.Role(
            name=name,
            description=description,
            is_superuser=is_superuser,
            is_staff=is_staff
        )
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return new_role
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(400, f"Error al crear el rol: {e.orig}")

@app.patch("/roles/{role_id}/", tags=["Roles"])
def update_role(role_id: int, name: str = None, description: str = None, db: Session = Depends(get_db)):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")
    if name:
        role.name = name.strip()
    if description is not None:
        role.description = description
    db.commit()
    db.refresh(role)
    return role

@app.delete("/roles/{role_id}/", tags=["Roles"])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")
    db.delete(role)
    db.commit()
    return {"detail": "Role deleted successfully"}

# Endpoints para Usuarios
@app.get("/users/", tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.name if user.role else "No role assigned",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
            "last_login": user.last_login
        }
        for user in users
    ]

@app.post("/users/", tags=["Users"])
def create_user(
    username: str,
    password: str,
    email: EmailStr,
    role_id: int,
    first_name: str = "",
    last_name: str = "",
    db: Session = Depends(get_db)
):
    # Verificación previa de duplicados
    existing_user = db.query(models.User).filter(
        (models.User.username == username) | (models.User.email == email)
    ).first()
    if existing_user:
        raise HTTPException(400, "Username or email already exists")

    # Obtener el rol y verificar sus propiedades
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")

    # Asignar valores heredados del rol
    hashed_password = pwd_context.hash(password)
    new_user = models.User(
        username=username,
        password=hashed_password,
        email=email,
        role_id=role_id,
        first_name=first_name,
        last_name=last_name,
        is_superuser=role.is_superuser,  # Heredado del rol
        is_staff=role.is_staff           # Heredado del rol
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "message": "User created successfully",
            "user_id": new_user.id,
            "is_superuser": new_user.is_superuser,
            "is_staff": new_user.is_staff
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(400, f"Error al crear el usuario: {e.orig}")


@app.patch("/users/{user_id}/", tags=["Users"])
def update_user(
    user_id: int,
    username: str = None,
    password: str = None,
    email: EmailStr = None,
    role_id: int = None,
    first_name: str = None,
    last_name: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if username:
        user.username = username
    if password:
        user.password = pwd_context.hash(password)
    if email:
        user.email = email
    if role_id:
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not role:
            raise HTTPException(404, "Role not found")
        user.role_id = role_id
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}/", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

# Endpoint de Autenticación
@app.post("/auth/login/", tags=["Auth"])
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(400, "Invalid credentials")
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
