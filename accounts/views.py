from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User, Role
import bcrypt  # Importar bcrypt para validación directa

# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

# Vista para administradores (ver lista completa de usuarios con acciones)
@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.all()  # Consultar todos los usuarios
    print(f"Usuarios (Admin View): {users}")  # Depuración
    return render(request, 'admin_user_list.html', {'users': users})

# Vista para usuarios de solo lectura (sin acciones)
@login_required
def read_only_user_list(request):
    users = User.objects.all()  # Consultar todos los usuarios
    print(f"Usuarios (Read-Only View): {users}")  # Depuración
    return render(request, 'read_only_user_list.html', {'users': users})

# Vista de inicio de sesión
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        print(f"Intento de inicio de sesión: Usuario={username}, Contraseña={password}")  # Depuración

        try:
            # Buscar usuario en la base de datos
            user = User.objects.get(username=username)
            print(f"Usuario encontrado en la base de datos: {user.username}")  # Depuración
            print(f"Contraseña en la base de datos: {user.password}")  # Depuración

            # Validar contraseña con bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                login(request, user)
                print(f"Usuario autenticado: {user.username}")  # Depuración
                # Redirigir según el rol del usuario
                if user.is_superuser:
                    return redirect('admin_user_list')
                else:
                    return redirect('read_only_user_list')
            else:
                print("Contraseña incorrecta")  # Depuración
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        except User.DoesNotExist:
            print("Usuario no encontrado")  # Depuración
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

# Vista para agregar un usuario (solo visible para administradores)
@login_required
@user_passes_test(is_admin)
def add_user(request):
    roles = Role.objects.all()  # Obtener todos los roles
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        role_id = request.POST['role_id']
        first_name = request.POST.get('first_name', "")
        last_name = request.POST.get('last_name', "")

        if not username or not password or not email or not role_id:
            return render(request, 'add_user.html', {'error': 'All fields are required', 'roles': roles})

        # Crear un usuario y cifrar la contraseña automáticamente
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User.objects.create(
            username=username,
            password=hashed_password,
            email=email,
            role_id=role_id,
            first_name=first_name,
            last_name=last_name
        )
        print(f"Usuario creado: {username}")  # Depuración
        return redirect('admin_user_list')

    return render(request, 'add_user.html', {'roles': roles})

# Vista para editar un usuario
@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)

        new_password = request.POST.get("password")
        if new_password:
            user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user.save()
        print(f"Usuario actualizado: {user.username}")  # Depuración
        return redirect('admin_user_list')

    return render(request, 'edit_user.html', {'user': user})

# Vista para eliminar un usuario
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        print(f"Usuario eliminado: {user.username}")  # Depuración
        return redirect('admin_user_list')

    return render(request, 'confirm_delete_user.html', {'user': user})

# Vista para cerrar sesión
@login_required
def user_logout(request):
    logout(request)
    print("Sesión cerrada")  # Depuración
    return redirect('user_login')  # Redirige al login después de cerrar sesión
