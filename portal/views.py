# scl_frontend_django/portal/views.py

import requests
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, ProductForm # Asegúrate de importar ProductForm

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

            except requests.exceptions.HTTPError as e_http:
                if e_http.response is not None:
                    if e_http.response.status_code == 401:
                        error_detail = "Nombre de usuario o contraseña incorrectos."
                        try:
                            error_detail = e_http.response.json().get('detail', error_detail)
                        except requests.exceptions.JSONDecodeError:
                            pass
                        messages.error(request, error_detail)
                    elif e_http.response.status_code == 400:
                        error_detail = "Error en la solicitud (ej: usuario inactivo)."
                        try:
                            error_detail = e_http.response.json().get('detail', error_detail)
                        except requests.exceptions.JSONDecodeError:
                            pass
                        messages.error(request, error_detail)
                    else:
                        messages.error(request, f'Error del servicio de autenticación: {e_http.response.status_code}')
                else:
                    messages.error(request, 'Error de HTTP sin respuesta del servidor.')
            except requests.exceptions.RequestException as e_req:
                messages.error(request, f'Error de red al intentar autenticar: {e_req}')
            except Exception as e_gen:
                messages.error(request, f'Ha ocurrido un error inesperado durante el login: {e_gen}')
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


# --- Vista de Dashboard (Muestra productos) ---
def dashboard_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')

    if not auth_token:
        messages.warning(request, 'Por favor, inicia sesión para acceder a esta página.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida para el dashboard.")
        return render(request, 'portal/dashboard.html', {
            'current_username': current_username,
            'products': [],
            'api_error': "Error de configuración interna (URL de API no encontrada)."
        })

    api_products_url = f"{fastapi_base_url}/products/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    products_list = []
    api_error_message = None

    try:
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
                return redirect('portal:login')
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
        'api_error': api_error_message
    }
    return render(request, 'portal/dashboard.html', context)

# --- Vista de Detalle del Producto ---
def product_detail_view(request, product_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')

    if not auth_token:
        messages.warning(request, 'Por favor, inicia sesión para ver detalles del producto.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida.")
        return redirect('portal:dashboard') 

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
                if 'auth_token' in request.session: del request.session['auth_token']
                if 'username' in request.session: del request.session['username']
                messages.error(request, api_error_message)
                return redirect('portal:login')
            elif e_http.response.status_code == 404:
                api_error_message = f"Producto con ID {product_id} no encontrado en la API."
            else:
                detail_error = ""
                try:
                    detail_error = e_http.response.json().get('detail', e_http.response.text)
                except requests.exceptions.JSONDecodeError:
                     detail_error = e_http.response.text
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
        'current_username': current_username
    }
    return render(request, 'portal/product_detail.html', context)

# --- Vista para Crear un Nuevo Producto ---
def product_create_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')

    if not auth_token:
        messages.error(request, 'Debes iniciar sesión para añadir un producto.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida.")
        return redirect('portal:dashboard')

    api_products_url = f"{fastapi_base_url}/products/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Para el método GET, pasamos el token al formulario para que pueda cargar las categorías
    # Para el método POST, también, por si hay errores y se vuelve a renderizar el formulario
    form_kwargs = {'api_auth_token': auth_token}

    if request.method == 'POST':
        form = ProductForm(request.POST, **form_kwargs)
        if form.is_valid():
            product_data_to_send = form.cleaned_data.copy()
            
            if not product_data_to_send.get('category_id'): # Si category_id es '' o None
                product_data_to_send['category_id'] = None
            else: # Asegurarse de que es un entero si se seleccionó algo
                try:
                    product_data_to_send['category_id'] = int(product_data_to_send['category_id'])
                except (ValueError, TypeError):
                    product_data_to_send['category_id'] = None # O manejar como error de formulario

            # Convertir DecimalField de Django a float para la API si es necesario
            if 'price' in product_data_to_send and product_data_to_send['price'] is not None:
                 product_data_to_send['price'] = float(product_data_to_send['price'])
            else: # Si el precio no es obligatorio y no se envía
                product_data_to_send.pop('price', None) # Eliminar si no se requiere o la API espera null

            try:
                response = requests.post(api_products_url, json=product_data_to_send, headers=headers)
                response.raise_for_status()
                
                new_product_api_response = response.json()
                messages.success(request, f"Producto '{new_product_api_response.get('name')}' creado exitosamente.")
                return redirect('portal:dashboard')

            except requests.exceptions.HTTPError as e_http:
                error_message = "Error al crear el producto en la API."
                if e_http.response is not None:
                    try:
                        api_error_details = e_http.response.json().get('detail')
                        if isinstance(api_error_details, list):
                            readable_errors = []
                            for error_item in api_error_details:
                                loc = " -> ".join(map(str, error_item.get('loc', ['body'])))
                                msg = error_item.get('msg', 'Error desconocido')
                                readable_errors.append(f"Campo '{loc}': {msg}")
                            error_message = "Error de validación de la API: " + "; ".join(readable_errors)
                        elif isinstance(api_error_details, str):
                             error_message = f"Error de API: {api_error_details}"
                        else:
                            error_message = f"Error de API ({e_http.response.status_code}): {e_http.response.text}"
                    except requests.exceptions.JSONDecodeError:
                        error_message = f"Error de API ({e_http.response.status_code}): Respuesta no es JSON válido."
                messages.error(request, error_message)
            except requests.exceptions.RequestException as e_req:
                messages.error(request, f"Error de red al crear el producto: {e_req}")
            except Exception as e_gen:
                messages.error(request, f"Un error inesperado ocurrió: {e_gen}")
            # Si hay error, el 'form' ya está poblado con request.POST, se volverá a renderizar
    else: # Petición GET
        form = ProductForm(**form_kwargs) # Pasa el token al inicializar para cargar categorías

    context = {
        'form': form,
        'current_username': current_username
    }
    return render(request, 'portal/product_form.html', context)