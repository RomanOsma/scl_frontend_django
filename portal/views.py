# scl_frontend_django/portal/views.py

import requests # Para hacer peticiones a la API FastAPI
from django.shortcuts import render, redirect
from django.contrib import messages # Para mostrar mensajes al usuario (ej: error de login)
from django.conf import settings # Para acceder a FASTAPI_BASE_URL
from .forms import LoginForm # Nuestro formulario de login

# --- Vista de Login ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Construir la URL del endpoint de token de la API FastAPI
            api_token_url = f"{settings.FASTAPI_BASE_URL}/auth/token"
            
            # Datos para enviar en el cuerpo de la solicitud (form-data)
            # OAuth2PasswordRequestForm espera 'username' y 'password' como claves.
            # La librería 'requests' los enviará como x-www-form-urlencoded por defecto si 'data' es un dict.
            auth_data = {
                'username': username,
                'password': password
                # 'grant_type': 'password' # FastAPI lo infiere, pero podrías añadirlo si tu API lo requiere estrictamente.
            }
            
            try:
                # Hacer la petición POST a la API FastAPI
                response = requests.post(api_token_url, data=auth_data)
                response.raise_for_status() # Lanza una excepción para códigos de error HTTP (4xx o 5xx)

                # Si la petición fue exitosa (200 OK)
                token_data = response.json() # Obtener el JSON de la respuesta
                
                # Almacenar el token en la sesión de Django
                # Esto es crucial para que el usuario permanezca "logueado" en el frontend
                # y para que podamos usar este token en futuras peticiones a la API.
                request.session['auth_token'] = token_data.get('access_token')
                request.session['username'] = username # Guardar también el username es útil
                
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect('portal:dashboard') # Redirigir a una página de 'dashboard' (la crearemos)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401: # Unauthorized
                    error_detail = e.response.json().get('detail', 'Nombre de usuario o contraseña incorrectos.')
                    messages.error(request, error_detail)
                elif e.response.status_code == 400: # Bad Request (ej: Usuario inactivo)
                    error_detail = e.response.json().get('detail', 'Error en la solicitud.')
                    messages.error(request, error_detail)
                else:
                    messages.error(request, f'Error al conectar con el servicio de autenticación: {e.response.status_code}')
            except requests.exceptions.RequestException as e:
                # Errores de conexión, timeout, etc.
                messages.error(request, f'Error de red al intentar autenticar: {e}')
            except Exception as e:
                # Otros errores inesperados
                messages.error(request, f'Ha ocurrido un error inesperado: {e}')
        else:
            # El formulario de Django no es válido (ej: campos vacíos si son required)
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else: # Si es una petición GET
        form = LoginForm() # Crear un formulario vacío

    return render(request, 'portal/login.html', {'form': form})


# --- Vista de Logout (Simple por ahora) ---
def logout_view(request):
    # Limpiar el token de la sesión
    if 'auth_token' in request.session:
        del request.session['auth_token']
    if 'username' in request.session:
        del request.session['username']
    
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('portal:login') # Redirigir a la página de login


# --- Vista de Dashboard (Placeholder por ahora) ---
# Necesitamos una vista a la que redirigir después del login.
def dashboard_view(request):
    # Verificar si el usuario está "logueado" (es decir, si hay un token en la sesión)
    if 'auth_token' not in request.session:
        messages.warning(request, 'Por favor, inicia sesión para acceder a esta página.')
        return redirect('portal:login')

    # Podríamos pasar el username a la plantilla si quisiéramos
    context = {
        'current_username': request.session.get('username')
    }
    return render(request, 'portal/dashboard.html', context)