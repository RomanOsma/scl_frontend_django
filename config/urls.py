# scl_frontend_django/config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.http import HttpResponse

# Vista de redirección raíz
def root_redirect_view(request):
    # Para probar, siempre redirige a login.
    # Cuando estés seguro de que la sesión funciona, puedes volver a la lógica condicional.
    return redirect('portal:login')
    # if request.user.is_authenticated and request.session.get('auth_token'):
    #     return redirect('portal:dashboard')
    # return redirect('portal:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')),
    path('', root_redirect_view, name='root_redirect'),
]