# scl_frontend_django/portal/urls.py

from django.urls import path
from . import views # Importa las vistas de la app portal

app_name = 'portal' # Define un espacio de nombres para estas URLs

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # Podríamos tener una vista para la raíz de la app portal, por ejemplo, que redirija al dashboard si está logueado
    # o al login si no lo está. O simplemente usar el dashboard como la "página de inicio" de la app.
    # path('', views.index_view, name='index'), 
]