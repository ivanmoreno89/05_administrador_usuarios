from django.urls import path
from . import views

urlpatterns = [
    # Vistas del Administrador y Lectura
    path('users/', views.admin_user_list, name='admin_user_list'),  # Vista completa (admin)
    path('users/read/', views.read_only_user_list, name='read_only_user_list'),  # Vista de solo lectura

    # Autenticación
    path('login/', views.user_login, name='user_login'),  # Inicio de sesión

    # Crear usuario (solo admin)
    path('users/add/', views.add_user, name='add_user'),  # Crear nuevo usuario

    # Editar usuario (solo admin)
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),  # Editar usuario

    # Eliminar usuario (solo admin)
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),  # Eliminar usuario

    # cerrar sesión
    path('logout/', views.user_logout, name='user_logout'), 
]
