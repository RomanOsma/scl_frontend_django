# scl_frontend_django/portal/views.py
import requests
import os
from django.shortcuts import render, redirect, get_object_or_404 # Añadido get_object_or_404 (aunque no lo usaremos directamente aquí con la API)
from django.contrib import messages
from .forms import LoginForm, ProductForm, CategoryForm

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

def logout_view(request):
    if 'auth_token' in request.session:
        del request.session['auth_token']
    if 'username' in request.session:
        del request.session['username']
    
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('portal:login')

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
    form_kwargs = {'api_auth_token': auth_token}

    if request.method == 'POST':
        form = ProductForm(request.POST, **form_kwargs)
        if form.is_valid():
            product_data_to_send = form.cleaned_data.copy()
            
            if not product_data_to_send.get('category_id'):
                product_data_to_send['category_id'] = None
            else:
                try:
                    product_data_to_send['category_id'] = int(product_data_to_send['category_id'])
                except (ValueError, TypeError):
                    product_data_to_send['category_id'] = None

            if 'price' in product_data_to_send and product_data_to_send['price'] is not None:
                 product_data_to_send['price'] = float(product_data_to_send['price'])
            else:
                product_data_to_send.pop('price', None)

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
                messages.error(request, f"Un error inesperado ocurrió creando producto: {e_gen}")
    else: 
        form = ProductForm(**form_kwargs)

    context = {
        'form': form,
        'is_editing': False, # Para la plantilla, indicar que es creación
        'current_username': current_username
    }
    return render(request, 'portal/product_form.html', context)

def product_update_view(request, product_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')

    if not auth_token:
        messages.error(request, 'Debes iniciar sesión para editar un producto.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida.")
        return redirect('portal:dashboard')

    api_product_url = f"{fastapi_base_url}/products/{product_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    form_kwargs = {'api_auth_token': auth_token}
    
    # Obtener datos del producto para pre-rellenar el formulario (si es GET)
    # o para tener una instancia base si el POST falla la validación
    product_instance_data = None
    try:
        response_get = requests.get(api_product_url, headers=headers)
        response_get.raise_for_status()
        product_instance_data = response_get.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"No se pudo obtener el producto a editar: {e}")
        return redirect('portal:dashboard')
    except Exception as e: # Captura cualquier otro error, como JSONDecodeError si la respuesta no es JSON
        messages.error(request, f"Error inesperado al obtener producto para editar: {e}")
        return redirect('portal:dashboard')

    if not product_instance_data: # Doble chequeo
        messages.error(request, f"Producto con ID {product_id} no encontrado para editar.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, **form_kwargs) # Validar los datos enviados
        if form.is_valid():
            product_data_to_send = form.cleaned_data.copy()

            if not product_data_to_send.get('category_id'):
                product_data_to_send['category_id'] = None
            else:
                try:
                    product_data_to_send['category_id'] = int(product_data_to_send['category_id'])
                except (ValueError, TypeError):
                    product_data_to_send['category_id'] = None
            
            if 'price' in product_data_to_send and product_data_to_send['price'] is not None:
                 product_data_to_send['price'] = float(product_data_to_send['price'])
            else:
                product_data_to_send.pop('price', None)
            
            # La API PUT espera todos los campos que se pueden modificar,
            # pero nuestro ProductUpdate schema en FastAPI permite campos opcionales.
            # Solo enviamos lo que está en el cleaned_data del formulario.
            # Si la API FastAPI usa un schema PATCH-like para PUT, esto funcionará bien.
            # Si la API FastAPI espera TODOS los campos en PUT, entonces necesitaríamos
            # fusionar product_instance_data con product_data_to_send aquí.
            # Por ahora, asumimos que la API maneja actualizaciones parciales en PUT.

            try:
                response_put = requests.put(api_product_url, json=product_data_to_send, headers=headers)
                response_put.raise_for_status()
                
                updated_product_api_response = response_put.json()
                messages.success(request, f"Producto '{updated_product_api_response.get('name')}' actualizado exitosamente.")
                return redirect('portal:product_detail', product_id=product_id) # Redirigir al detalle del producto actualizado

            except requests.exceptions.HTTPError as e_http:
                error_message = "Error al actualizar el producto en la API."
                # (Mismo manejo de errores que en create_view)
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
                messages.error(request, f"Error de red al actualizar el producto: {e_req}")
            except Exception as e_gen:
                messages.error(request, f"Un error inesperado ocurrió actualizando producto: {e_gen}")
            # Si hay error, el 'form' ya está poblado con request.POST, se volverá a renderizar
    else: # Petición GET
        # Pre-rellenar el formulario con los datos del producto existente
        # Asegurarse de que los nombres de los campos coincidan con los del ProductForm
        initial_data = {
            'name': product_instance_data.get('name'),
            'description': product_instance_data.get('description'),
            'price': product_instance_data.get('price'),
            'stock_actual': product_instance_data.get('stock_actual'),
            'stock_minimo': product_instance_data.get('stock_minimo'),
            'codigo_sku': product_instance_data.get('codigo_sku'),
            'numero_serie': product_instance_data.get('numero_serie'),
            'category_id': product_instance_data.get('category', {}).get('id') if product_instance_data.get('category') else None
        }
        form = ProductForm(initial=initial_data, **form_kwargs)

    context = {
        'form': form,
        'is_editing': True, # Para la plantilla, indicar que es edición
        'product_id': product_id, # Para la URL del action del form si es necesario, o para título
        'current_username': current_username
    }
    return render(request, 'portal/product_form.html', context)

def product_delete_view(request, product_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username') # Para pasarlo a la plantilla si es necesario

    if not auth_token:
        messages.error(request, 'Debes iniciar sesión para eliminar un producto.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida.")
        return redirect('portal:dashboard')

    api_product_url = f"{fastapi_base_url}/products/{product_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    product_to_delete = None
    api_error_message = None

    # Primero, obtener el producto para mostrar su nombre en la confirmación
    try:
        response_get = requests.get(api_product_url, headers=headers)
        response_get.raise_for_status()
        product_to_delete = response_get.json()
    except requests.exceptions.HTTPError as e_http:
        # ... (Manejo de errores similar a product_detail_view para GET) ...
        if e_http.response is not None:
            if e_http.response.status_code == 401: # Sesión expirada o inválida
                messages.error(request, "Tu sesión ha expirado. Por favor, inicia sesión de nuevo.")
                if 'auth_token' in request.session: del request.session['auth_token']
                if 'username' in request.session: del request.session['username']
                return redirect('portal:login')
            elif e_http.response.status_code == 404:
                messages.error(request, f"Producto con ID {product_id} no encontrado para eliminar.")
            else:
                messages.error(request, f"Error ({e_http.response.status_code}) al obtener el producto para eliminar.")
        else:
            messages.error(request, "Error de HTTP sin respuesta al obtener producto.")
        return redirect('portal:dashboard') # Redirigir si no se puede obtener el producto
    except requests.exceptions.RequestException:
        messages.error(request, "Error de red al intentar obtener el producto para eliminar.")
        return redirect('portal:dashboard')

    if not product_to_delete: # Doble chequeo por si acaso
         messages.error(request, f"No se pudo encontrar el producto con ID {product_id}.")
         return redirect('portal:dashboard')

    if request.method == 'POST':
        # El usuario ha confirmado la eliminación
        try:
            response_delete = requests.delete(api_product_url, headers=headers)
            response_delete.raise_for_status() # Lanza error para 4xx/5xx

            # Si la API devuelve el objeto eliminado (como lo configuramos):
            # deleted_product_name = response_delete.json().get('name', 'el producto')
            # messages.success(request, f"Producto '{deleted_product_name}' eliminado exitosamente.")
            # O si es 204 No Content:
            messages.success(request, f"Producto '{product_to_delete.get('name', 'ID '+str(product_id))}' eliminado exitosamente.")
            return redirect('portal:dashboard')

        except requests.exceptions.HTTPError as e_http:
            error_message = "Error al eliminar el producto en la API."
            if e_http.response is not None:
                try:
                    api_error_details = e_http.response.json().get('detail')
                    if isinstance(api_error_details, str):
                        error_message = f"Error de API: {api_error_details}"
                    else: # Error 500 o no JSON
                        error_message = f"Error de API ({e_http.response.status_code}): {e_http.response.text}"
                except requests.exceptions.JSONDecodeError:
                    error_message = f"Error de API ({e_http.response.status_code}): Respuesta no es JSON válido."
            messages.error(request, error_message)
            # Volver a la página de confirmación o al dashboard
            return redirect('portal:product_detail', product_id=product_id) 
        except requests.exceptions.RequestException as e_req:
            messages.error(request, f"Error de red al eliminar el producto: {e_req}")
            return redirect('portal:product_detail', product_id=product_id)
        except Exception as e_gen:
            messages.error(request, f"Un error inesperado ocurrió al eliminar el producto: {e_gen}")
            return redirect('portal:product_detail', product_id=product_id)
    
    # Si es una petición GET, mostrar la página de confirmación
    context = {
        'product': product_to_delete,
        'current_username': current_username
    }
    return render(request, 'portal/product_confirm_delete.html', context)

def category_create_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')

    if not auth_token:
        messages.error(request, 'Debes iniciar sesión para añadir una categoría.')
        return redirect('portal:login')

    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    if not fastapi_base_url:
        messages.error(request, "Error de configuración: URL de la API no definida.")
        return redirect('portal:dashboard') # O a una página de error de configuración

    api_categories_url = f"{fastapi_base_url}/categories/"
    headers = {'Authorization': f'Bearer {auth_token}'}

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_data_to_send = form.cleaned_data.copy()
            try:
                response = requests.post(api_categories_url, json=category_data_to_send, headers=headers)
                response.raise_for_status()
                
                new_category_api_response = response.json()
                messages.success(request, f"Categoría '{new_category_api_response.get('name')}' creada exitosamente.")
                # Podríamos redirigir a una lista de categorías o al dashboard
                return redirect('portal:dashboard') 

            except requests.exceptions.HTTPError as e_http:
                error_message = "Error al crear la categoría en la API."
                if e_http.response is not None:
                    try:
                        api_error_details = e_http.response.json().get('detail')
                        if isinstance(api_error_details, list): # Errores de validación Pydantic
                            readable_errors = []
                            for error_item in api_error_details:
                                loc = " -> ".join(map(str, error_item.get('loc', ['body'])))
                                msg = error_item.get('msg', 'Error desconocido')
                                readable_errors.append(f"Campo '{loc}': {msg}")
                            error_message = "Error de validación de la API: " + "; ".join(readable_errors)
                        elif isinstance(api_error_details, str): # Otros errores de la API (ej: nombre duplicado)
                             error_message = f"Error de API: {api_error_details}"
                        else:
                            error_message = f"Error de API ({e_http.response.status_code}): {e_http.response.text}"
                    except requests.exceptions.JSONDecodeError:
                        error_message = f"Error de API ({e_http.response.status_code}): Respuesta no es JSON válido."
                messages.error(request, error_message)
            except requests.exceptions.RequestException as e_req:
                messages.error(request, f"Error de red al crear la categoría: {e_req}")
            except Exception as e_gen:
                messages.error(request, f"Un error inesperado ocurrió creando la categoría: {e_gen}")
            # Si hay error, el 'form' ya está poblado con request.POST, se volverá a renderizar
    else: # Petición GET
        form = CategoryForm()

    context = {
        'form': form,
        'form_title': 'Añadir Nueva Categoría', # Para la plantilla
        'current_username': current_username
    }
    # Reutilizaremos la plantilla product_form.html para categorías por simplicidad,
    # o podrías crear una category_form.html muy similar.
    return render(request, 'portal/category_form.html', context) # Usaremos una nueva plantilla



