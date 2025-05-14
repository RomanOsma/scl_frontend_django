# scl_frontend_django/portal/views.py

import requests
import os
from django.shortcuts import render, redirect
from django.contrib import messages
# from django.conf import settings # No lo necesitamos si usamos os.getenv directamente
from .forms import LoginForm

# --- Vista de Login ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
            if not fastapi_base_url:
                messages.error(request, "Error de configuración: URL de la API no definida.")
                return render(request, 'portal/login.html', {'form': form})

            api_token_url = f"{fastapi_base_url}/auth/token"
            auth_data = {'username': username, 'password': password}
            
            try:
                response = requests.post(api_token_url, data=auth_data)
                response.raise_for_status() 
                token_data = response.json()
                
                request.session['auth_token'] = token_data.get('access_token')
                request.session['username'] = username 
                
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect('portal:dashboard')

            except requests.exceptions.HTTPError as e:
                if e.response is not None: # Verificar que e.response exista
                    if e.response.status_code == 401:
                        error_detail = "Nombre de usuario o contraseña incorrectos."
                        try: # Intentar obtener el detalle de la API
                            error_detail = e.response.json().get('detail', error_detail)
                        except requests.exceptions.JSONDecodeError:
                            pass # Mantener el mensaje genérico si el cuerpo no es JSON
                        messages.error(request, error_detail)
                    elif e.response.status_code == 400:
                        error_detail = "Error en la solicitud (ej: usuario inactivo)."
                        try:
                            error_detail = e.response.json().get('detail', error_detail)
                        except requests.exceptions.JSONDecodeError:
                            pass
                        messages.error(request, error_detail)
                    else:
                        messages.error(request, f'Error del servicio de autenticación: {e.response.status_code}')
                else:
                    messages.error(request, 'Error de HTTP sin respuesta del servidor.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de red al intentar autenticar: {e}')
            except Exception as e:
                messages.error(request, f'Ha ocurrido un error inesperado durante el login: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else: 
        form = LoginForm()

    return render(request, 'portal/login.html', {'form': form})


# --- Vista de Logout ---
def logout_view(request):
    if 'auth_token' in request.session:
        del request.session['auth_token']
    if 'username' in request.session:
        del request.session['username']
    
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('portal:login')


# --- Vista de Dashboard (MODIFICADA para mostrar productos) ---
def dashboard_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')

    if not auth_token:
        messages.warning(request, 'Por favor, inicia sesión para acceder a esta página.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida para el dashboard.")
        # Renderizar el dashboard pero indicando el error de configuración
        return render(request, 'portal/dashboard.html', {
            'current_username': current_username,
            'products': [],
            'api_error': "Error de configuración interna (URL de API no encontrada)."
        })

    api_products_url = f"{fastapi_base_url}/products/"
    
    headers = {
        'Authorization': f'Bearer {auth_token}'
        # Nota: Para el GET /products/, el token no es estrictamente necesario
        # según nuestra configuración actual del backend, pero lo incluimos
        # por si en el futuro se protege o para otros GETs que sí lo requieran.
    }

    products_list = []
    api_error_message = None # Renombrado para evitar conflicto con la variable de excepción 'e'

    try:
        # Añadimos parámetros de paginación por defecto
        params = {'skip': 0, 'limit': 100}
        response = requests.get(api_products_url, headers=headers, params=params)
        response.raise_for_status()
        products_list = response.json()

    except requests.exceptions.HTTPError as e_http:
        if e_http.response is not None:
            if e_http.response.status_code == 401:
                api_error_message = "Tu sesión ha expirado o es inválida. Por favor, inicia sesión de nuevo."
                if 'auth_token' in request.session: del request.session['auth_token']
                if 'username' in request.session: del request.session['username']
                messages.error(request, api_error_message)
                return redirect('portal:login') # Forzar re-login
            else:
                detail_error = ""
                try:
                    detail_error = e_http.response.json().get('detail', e_http.response.text)
                except requests.exceptions.JSONDecodeError:
                    detail_error = e_http.response.text
                api_error_message = f"Error al obtener productos de la API: {e_http.response.status_code} - {detail_error}"
        else:
            api_error_message = "Error de HTTP sin respuesta del servidor al obtener productos."
        messages.error(request, api_error_message)
    except requests.exceptions.RequestException as e_req:
        api_error_message = f"Error de red al conectar con la API de productos: {e_req}"
        messages.error(request, api_error_message)
    except Exception as e_gen:
        api_error_message = f"Un error inesperado ocurrió al obtener productos: {e_gen}"
        messages.error(request, api_error_message)

    context = {
        'current_username': current_username,
        'products': products_list,
        'api_error': api_error_message # Pasamos el mensaje de error a la plantilla
    }
    return render(request, 'portal/dashboard.html', context)

def product_detail_view(request, product_id):
    auth_token = request.session.get('auth_token')
    # Aunque el GET de un producto no está protegido, incluimos el token
    # por si en el futuro se protege o para consistencia.
    # Si no hay token y el endpoint es público, igual funcionaría sin él.
    if not auth_token: # Podrías permitir acceso público si el endpoint API lo permite
        messages.warning(request, 'Por favor, inicia sesión para ver detalles del producto.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida.")
        return redirect('portal:dashboard') # O a una página de error

    api_product_url = f"{fastapi_base_url}/products/{product_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    product_data = None
    api_error_message = None

    try:
        response = requests.get(api_product_url, headers=headers)
        response.raise_for_status()
        product_data = response.json()
    except requests.exceptions.HTTPError as e_http:
        if e_http.response is not None:
            if e_http.response.status_code == 401:
                api_error_message = "Tu sesión ha expirado o es inválida. Por favor, inicia sesión de nuevo."
                # Limpiar sesión y redirigir
                if 'auth_token' in request.session: del request.session['auth_token']
                if 'username' in request.session: del request.session['username']
                messages.error(request, api_error_message)
                return redirect('portal:login')
            elif e_http.response.status_code == 404:
                api_error_message = f"Producto con ID {product_id} no encontrado en la API."
            else:
                detail_error = e_http.response.json().get('detail', e_http.response.text)
                api_error_message = f"Error al obtener el producto de la API: {e_http.response.status_code} - {detail_error}"
        else:
            api_error_message = "Error de HTTP sin respuesta del servidor al obtener el producto."
        messages.error(request, api_error_message)
    except requests.exceptions.RequestException as e_req:
        api_error_message = f"Error de red al conectar con la API: {e_req}"
        messages.error(request, api_error_message)
    except Exception as e_gen:
        api_error_message = f"Un error inesperado ocurrió: {e_gen}"
        messages.error(request, api_error_message)
        
    context = {
        'product': product_data,
        'api_error': api_error_message,
        'current_username': request.session.get('username')
    }
    return render(request, 'portal/product_detail.html', context) # Comentado
    # return render(request, 'portal/test_p_detail.html', context) # Línea de prueba