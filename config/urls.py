"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# scl_frontend_django/config/urls.py

from django.contrib import admin
from django.urls import path, include # ¡Asegúrate de importar 'include'!
from django.shortcuts import redirect # Para la redirección raíz

# Una vista simple para la raíz del sitio
def root_redirect_view(request):
    if request.user.is_authenticated and request.session.get('auth_token'): # Un poco redundante pero seguro
        return redirect('portal:dashboard')
    return redirect('portal:login')

urlpatterns = [
     path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')), # ¡NUEVO! Incluye las URLs de la app portal
    path('', root_redirect_view, name='root_redirect'), # ¡NUEVO! Redirige la raíz del sitio
]
