# scl_frontend_django/portal/views.py
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
# from django.conf import settings # Ya no necesitas importar settings para esto
import os # ¡AÑADIDO!
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            print(f"Intentando obtener FASTAPI_BASE_URL. Valor actual: '{os.getenv('FASTAPI_BASE_URL')}'") # Línea de depuración
            # Leer la URL base de la API FastAPI desde las variables de entorno
            fastapi_url = os.getenv('FASTAPI_BASE_URL') # ¡CAMBIADO!
            if not fastapi_url:
                messages.error(request, "Error de configuración: URL de la API no definida.")
                return render(request, 'portal/login.html', {'form': form})

            api_token_url = f"{fastapi_url}/auth/token" # ¡CAMBIADO!
            
            auth_data = {
                'username': username,
                'password': password
            }
            # ... (resto de la lógica try/except como antes) ...
            try:
                response = requests.post(api_token_url, data=auth_data)
                response.raise_for_status() 
                token_data = response.json()
                request.session['auth_token'] = token_data.get('access_token')
                request.session['username'] = username 
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect('portal:dashboard')
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    error_detail = e.response.json().get('detail', 'Nombre de usuario o contraseña incorrectos.')
                    messages.error(request, error_detail)
                elif e.response.status_code == 400:
                    error_detail = e.response.json().get('detail', 'Error en la solicitud.')
                    messages.error(request, error_detail)
                else:
                    messages.error(request, f'Error al conectar con el servicio de autenticación: {e.response.status_code}')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de red al intentar autenticar: {e}')
            except Exception as e:
                messages.error(request, f'Ha ocurrido un error inesperado: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else: 
        form = LoginForm()
    return render(request, 'portal/login.html', {'form': form})

# ... (logout_view y dashboard_view como antes) ...
def logout_view(request):
    if 'auth_token' in request.session:
        del request.session['auth_token']
    if 'username' in request.session:
        del request.session['username']
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('portal:login')

def dashboard_view(request):
    if 'auth_token' not in request.session:
        messages.warning(request, 'Por favor, inicia sesión para acceder a esta página.')
        return redirect('portal:login')
    context = {
        'current_username': request.session.get('username')
    }
    return render(request, 'portal/dashboard.html', context)