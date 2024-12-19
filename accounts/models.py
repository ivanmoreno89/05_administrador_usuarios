from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "roles"  # Nombre de la tabla compartida con FastAPI
        managed = False     # Evita que Django modifique la tabla existente

    def __str__(self):
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)  # Coincide con FastAPI
    last_name = models.CharField(max_length=150, blank=True, null=True)   # Coincide con FastAPI

    class Meta:
        db_table = "users"  # Nombre de la tabla compartida con FastAPI
        managed = False     # Evita que Django modifique la tabla existente

    def __str__(self):
        return self.username
