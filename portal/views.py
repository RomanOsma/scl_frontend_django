# scl_frontend_django/portal/views.py
import requests
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, ProductForm, CategoryForm

# --- login_view, logout_view, dashboard_view ---
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
                error_detail = "Error de autenticación."
                if e_http.response is not None:
                    if e_http.response.status_code == 401: error_detail = "Nombre de usuario o contraseña incorrectos."
                    try: error_detail = e_http.response.json().get('detail', error_detail)
                    except: pass
                messages.error(request, error_detail)
            except Exception as e: messages.error(request, f'Error: {e}')
        else: messages.error(request, 'Formulario inválido.')
    else: form = LoginForm()
    return render(request, 'portal/login.html', {'form': form})

def logout_view(request):
    if 'auth_token' in request.session: del request.session['auth_token']
    if 'username' in request.session: del request.session['username']
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('portal:login')

def dashboard_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token:
        messages.warning(request, 'Por favor, inicia sesión.')
        return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    products_list = []
    api_error_message = None
    if fastapi_base_url:
        api_products_url = f"{fastapi_base_url}/products/"
        headers = {'Authorization': f'Bearer {auth_token}'}
        try:
            response = requests.get(api_products_url, headers=headers, params={'limit': 100})
            response.raise_for_status()
            products_list = response.json()
        except Exception as e:
            api_error_message = f"Error obteniendo productos: {e}"
            # Intentar obtener un mensaje más específico de la API si es un HTTPError
            if hasattr(e, 'response') and e.response is not None:
                try:
                    detail = e.response.json().get('detail', str(e))
                    api_error_message = f"Error API ({e.response.status_code}): {detail}"
                except: # Si no se puede parsear JSON
                    api_error_message = f"Error API ({e.response.status_code}): {e.response.text}"
            messages.error(request, api_error_message)
    else:
        api_error_message = "URL de API no configurada."
        messages.error(request, api_error_message)
    context = {'current_username': current_username, 'products': products_list, 'api_error': api_error_message}
    return render(request, 'portal/dashboard.html', context)

# --- CRUD PRODUCTOS ---
def product_create_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_products_url = f"{fastapi_base_url}/products/"
    headers = {'Authorization': f'Bearer {auth_token}'}

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            if not data.get('category_id'): 
                data['category_id'] = None
            
            # Convertir Decimal a float para JSON serializable
            if data.get('price') is not None:
                data['price'] = float(data['price']) # <--- CORRECCIÓN
            else:
                 data.pop('price', None) # Si es None y la API no lo quiere, se elimina

            try:
                response = requests.post(api_products_url, json=data, headers=headers)
                response.raise_for_status()
                messages.success(request, f"Producto '{response.json().get('name')}' creado.")
                return redirect('portal:dashboard')
            except requests.exceptions.HTTPError as e:
                error_detail = "Error API creando producto."
                if e.response is not None:
                    try: 
                        detail = e.response.json().get('detail')
                        if isinstance(detail, list):
                            readable_errors = [f"Campo {' -> '.join(map(str, err.get('loc',[])))}: {err.get('msg','')}" for err in detail]
                            error_detail = "Errores de validación: " + "; ".join(readable_errors)
                        elif isinstance(detail, str):
                            error_detail = detail
                        else:
                             error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                    except:  error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                messages.error(request, error_detail)
            except Exception as e: messages.error(request, f"Error inesperado: {e}")
        else:
            messages.error(request, "Formulario inválido. Por favor, revisa los campos.")
    else:
        form = ProductForm()
    
    context = {'form': form, 'is_editing': False, 'current_username': current_username, 'form_title': "Crear Producto"}
    return render(request, 'portal/product_form.html', context)

def product_detail_view(request, product_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_url = f"{fastapi_base_url}/products/{product_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    product = None
    api_error_message = None # Renombrado para evitar confusión con la variable 'error'
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        product = response.json()
    except Exception as e:
        api_error_message = f"Error obteniendo producto ({product_id})."
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 404: api_error_message = f"Producto con ID {product_id} no encontrado."
            try: api_error_message = e.response.json().get('detail', api_error_message)
            except: pass
        else: api_error_message = str(e)
        messages.error(request, api_error_message)
    context = {'product': product, 'api_error': api_error_message, 'current_username': current_username}
    return render(request, 'portal/product_detail.html', context)

def product_update_view(request, product_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_url = f"{fastapi_base_url}/products/{product_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    product_name_for_title = f"ID {product_id}" # Fallback para el título

    # Obtener datos del producto para el título y para rellenar el form en GET
    try:
        response_get_initial = requests.get(api_url, headers=headers)
        response_get_initial.raise_for_status()
        product_initial_data_api = response_get_initial.json()
        product_name_for_title = product_initial_data_api.get('name', product_name_for_title)
    except Exception as e:
        messages.error(request, f"Error cargando datos del producto para editar: {e}")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            if not data.get('category_id'): 
                data['category_id'] = None
            
            # Convertir Decimal a float para JSON serializable
            if data.get('price') is not None:
                data['price'] = float(data['price']) # <--- CORRECCIÓN
            else:
                data.pop('price', None)
            
            try:
                response = requests.put(api_url, json=data, headers=headers)
                response.raise_for_status()
                messages.success(request, f"Producto '{response.json().get('name')}' actualizado.")
                return redirect('portal:product_detail', product_id=product_id)
            except requests.exceptions.HTTPError as e:
                error_detail = "Error API actualizando producto."
                if e.response is not None:
                    try: 
                        detail = e.response.json().get('detail')
                        if isinstance(detail, list): 
                            readable_errors = [f"Campo {' -> '.join(map(str, err.get('loc',[])))}: {err.get('msg','')}" for err in detail]
                            error_detail = "Errores de validación: " + "; ".join(readable_errors)
                        elif isinstance(detail, str):
                            error_detail = detail
                        else:
                             error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                    except: error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                messages.error(request, error_detail)
            except Exception as e: messages.error(request, f"Error inesperado: {e}")
        else: 
            messages.error(request, "Formulario inválido. Por favor, revisa los campos.")
            # product_name_for_title ya se obtuvo antes del bloque POST
    else: # Petición GET
        # product_initial_data_api ya se obtuvo antes
        initial_form_data = {
            'name': product_initial_data_api.get('name'), 
            'description': product_initial_data_api.get('description'),
            'price': product_initial_data_api.get('price'), 
            'stock_actual': product_initial_data_api.get('stock_actual'),
            'stock_minimo': product_initial_data_api.get('stock_minimo'), 
            'codigo_sku': product_initial_data_api.get('codigo_sku'),
            'numero_serie': product_initial_data_api.get('numero_serie'),
            'category_id': product_initial_data_api.get('category', {}).get('id') if product_initial_data_api.get('category') else None
        }
        form = ProductForm(initial=initial_form_data)
    
    context = {
        'form': form, 'is_editing': True, 'product_id': product_id, 
        'form_title': f"Editar: {product_name_for_title}",
        'current_username': current_username
    }
    return render(request, 'portal/product_form.html', context)

def product_delete_view(request, product_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_url = f"{fastapi_base_url}/products/{product_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    item_to_delete = None
    try: 
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        item_to_delete = response.json()
    except Exception as e:
        messages.error(request, f"Error obteniendo producto para eliminar: {e}")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        try:
            response_del = requests.delete(api_url, headers=headers)
            response_del.raise_for_status()
            messages.success(request, f"Producto '{item_to_delete.get('name', product_id)}' eliminado.")
            return redirect('portal:dashboard')
        except Exception as e:
            error_detail = "Error API eliminando producto."
            if hasattr(e, 'response') and e.response is not None:
                try: error_detail = e.response.json().get('detail', f"Error ({e.response.status_code})")
                except: error_detail = f"Error ({e.response.status_code}): {e.response.text}"
            else: error_detail = str(e)
            messages.error(request, error_detail)
            return redirect('portal:product_detail', product_id=product_id) if item_to_delete else redirect('portal:dashboard')

    context = {
        'item': item_to_delete, 'item_type': 'Producto', 'current_username': current_username,
        'cancel_url_info': {'name': 'portal:product_detail', 'pk': product_id} if item_to_delete else {'name': 'portal:dashboard'}
    }
    return render(request, 'portal/confirm_delete.html', context)

# --- CRUD CATEGORÍAS ---
def category_list_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_url = f"{fastapi_base_url}/categories/"
    headers = {'Authorization': f'Bearer {auth_token}'} 
    categories, api_error_message = [], None # Renombrado error a api_error_message
    try:
        response = requests.get(api_url, headers=headers, params={'limit': 100})
        response.raise_for_status()
        categories = response.json()
    except Exception as e:
        api_error_message = f"Error obteniendo categorías: {e}"
        if hasattr(e, 'response') and e.response is not None:
                try: api_error_message = e.response.json().get('detail', f"Error ({e.response.status_code})")
                except: api_error_message = f"Error ({e.response.status_code}): {e.response.text}"
        messages.error(request, api_error_message)
    context = {'categories': categories, 'api_error': api_error_message, 'current_username': current_username}
    return render(request, 'portal/category_list.html', context)

def category_create_view(request):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_url = f"{fastapi_base_url}/categories/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                response = requests.post(api_url, json=form.cleaned_data, headers=headers)
                response.raise_for_status()
                messages.success(request, f"Categoría '{response.json().get('name')}' creada.")
                return redirect('portal:category_list')
            except requests.exceptions.HTTPError as e:
                error_detail = "Error API creando categoría."
                # ... (manejo de errores detallado) ...
                if e.response is not None:
                    try: 
                        detail = e.response.json().get('detail')
                        if isinstance(detail, list): 
                            readable_errors = [f"Campo {' -> '.join(map(str, err.get('loc',[])))}: {err.get('msg','')}" for err in detail]
                            error_detail = "Errores de validación: " + "; ".join(readable_errors)
                        elif isinstance(detail, str):
                            error_detail = detail
                        else:
                             error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                    except: error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                messages.error(request, error_detail)
            except Exception as e: messages.error(request, f"Error inesperado: {e}")
        else:
            messages.error(request, "Formulario inválido. Por favor, revisa los campos.")
    else: form = CategoryForm()
    context = {'form': form, 'is_editing': False, 'form_title': "Crear Categoría", 'current_username': current_username}
    return render(request, 'portal/category_form.html', context)

def category_update_view(request, category_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_url = f"{fastapi_base_url}/categories/{category_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    category_name_for_title = f"ID {category_id}" # Fallback

    try:
        response_get_initial = requests.get(api_url, headers=headers)
        response_get_initial.raise_for_status()
        category_initial_data_api = response_get_initial.json()
        category_name_for_title = category_initial_data_api.get('name', category_name_for_title)
    except Exception as e:
        messages.error(request, f"Error cargando datos de la categoría para editar: {e}")
        return redirect('portal:category_list')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                response = requests.put(api_url, json=form.cleaned_data, headers=headers)
                response.raise_for_status()
                messages.success(request, f"Categoría '{response.json().get('name')}' actualizada.")
                return redirect('portal:category_list')
            except requests.exceptions.HTTPError as e:
                error_detail = "Error API actualizando categoría."
                # ... (manejo de errores detallado) ...
                if e.response is not None:
                    try: 
                        detail = e.response.json().get('detail')
                        if isinstance(detail, list): 
                            readable_errors = [f"Campo {' -> '.join(map(str, err.get('loc',[])))}: {err.get('msg','')}" for err in detail]
                            error_detail = "Errores de validación: " + "; ".join(readable_errors)
                        elif isinstance(detail, str):
                            error_detail = detail
                        else:
                             error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                    except: error_detail = f"Error ({e.response.status_code}): {e.response.text}"
                messages.error(request, error_detail)
            except Exception as e: messages.error(request, f"Error inesperado: {e}")
        else:
            messages.error(request, "Formulario inválido. Por favor, revisa los campos.")
            # category_name_for_title ya está definida
    else: # GET
        form = CategoryForm(initial=category_initial_data_api)
    
    context = {
        'form': form, 'is_editing': True, 'category_id': category_id, 
        'form_title': f"Editar: {category_name_for_title}",
        'current_username': current_username
    }
    return render(request, 'portal/category_form.html', context)

def category_delete_view(request, category_id):
    auth_token = request.session.get('auth_token')
    current_username = request.session.get('username')
    if not auth_token: return redirect('portal:login')
    fastapi_base_url = os.getenv('FASTAPI_BASE_URL')
    api_url = f"{fastapi_base_url}/categories/{category_id}/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    item_to_delete = None
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        item_to_delete = response.json()
    except Exception as e:
        messages.error(request, f"Error obteniendo categoría para eliminar: {e}")
        return redirect('portal:category_list')

    if request.method == 'POST':
        try:
            response_del = requests.delete(api_url, headers=headers)
            response_del.raise_for_status()
            messages.success(request, f"Categoría '{item_to_delete.get('name', category_id)}' eliminada.")
            return redirect('portal:category_list')
        except Exception as e:
            error_detail = "Error API eliminando categoría."
            if hasattr(e, 'response') and e.response is not None:
                try: error_detail = e.response.json().get('detail', f"Error ({e.response.status_code})")
                except: error_detail = f"Error ({e.response.status_code}): {e.response.text}"
            else: error_detail = str(e)
            messages.error(request, error_detail)
            return redirect('portal:category_list')

    context = {
        'item': item_to_delete, 'item_type': 'Categoría', 'current_username': current_username,
        'cancel_url_info': {'name': 'portal:category_list'}
    }
    return render(request, 'portal/confirm_delete.html', context)