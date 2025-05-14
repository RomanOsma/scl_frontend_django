# scl_frontend_django/portal/forms.py
from django import forms
# Si necesitas obtener opciones para un ChoiceField desde la BD (ej: categorías),
# lo haríamos de forma diferente, pero por ahora, el category_id será un IntegerField.

class LoginForm(forms.Form):
    # ... (tu LoginForm como antes) ...
    username = forms.CharField(
        label="Nombre de Usuario",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre de usuario'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Tu contraseña'})
    )

class ProductForm(forms.Form):
    name = forms.CharField(
        label="Nombre del Producto", 
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Descripción", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 
        required=False # La API lo permite opcional
    )
    price = forms.DecimalField( # Usar DecimalField para precios es mejor que FloatField
        label="Precio", 
        max_digits=10, 
        decimal_places=2,
        min_value=0.01, # Validación básica
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    stock_actual = forms.IntegerField(
        label="Stock Actual", 
        min_value=0, 
        initial=0, # Valor inicial
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    stock_minimo = forms.IntegerField(
        label="Stock Mínimo", 
        min_value=0, 
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    codigo_sku = forms.CharField(
        label="Código SKU", 
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_serie = forms.CharField(
        label="Número de Serie (si aplica)", 
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Para category_id, idealmente sería un ChoiceField que se pueble con las categorías
    # obtenidas de la API. Por ahora, para simplificar el primer paso, lo haremos
    # como un IntegerField y el usuario tendría que saber el ID.
    # Más adelante lo podemos mejorar.
    category_id = forms.IntegerField(
        label="ID de Categoría (Opcional)", 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Dejar en blanco si no tiene categoría."
    )

    # Podríamos añadir proveedor_id de forma similar si lo necesitáramos en este formulario.
    # proveedor_id = forms.IntegerField(label="ID de Proveedor (Opcional)", required=False)

    def __init__(self, *args, **kwargs):
        # Podríamos pasar una lista de opciones de categorías aquí si las obtenemos de la API
        # category_choices = kwargs.pop('category_choices', None)
        super().__init__(*args, **kwargs)
        # if category_choices:
        #     self.fields['category_id'].choices = category_choices