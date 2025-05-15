# scl_frontend_django/portal/urls.py

from django.urls import path
from . import views # Importa las vistas de la app portal

app_name = 'portal' # Define un espacio de nombres para estas URLs

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('product/add/', views.product_create_view, name='product_add'),
    path('product/<int:product_id>/edit/', views.product_update_view, name='product_edit'),
    path('product/<int:product_id>/delete/', views.product_delete_view, name='product_delete'),
    path('category/add/', views.category_create_view, name='category_add'),
    path('category/', views.category_list_view, name='category_list'),
    path('category/<int:category_id>/edit/', views.category_update_view, name='category_edit'),
    path('category/<int:category_id>/delete/', views.category_delete_view, name='category_delete'),
]