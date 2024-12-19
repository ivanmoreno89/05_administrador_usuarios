from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Administrador de Django
    path('admin/', admin.site.urls),

    # Aplicación Accounts
    path('accounts/', include('accounts.urls')),
]
