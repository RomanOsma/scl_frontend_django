# scl_frontend_django/portal/forms.py
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de Usuario", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre de usuario'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Tu contraseña'}))

class ProductForm(forms.Form):
    name = forms.CharField(label="Nombre del Producto", max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label="Descripción", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    price = forms.DecimalField(label="Precio", max_digits=10, decimal_places=2, min_value=0.01, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), required=False)
    stock_actual = forms.IntegerField(label="Stock Actual", min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    stock_minimo = forms.IntegerField(label="Stock Mínimo", min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    codigo_sku = forms.CharField(label="Código SKU", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero_serie = forms.CharField(label="Número de Serie (si aplica)", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category_id = forms.IntegerField(label="ID de Categoría (Opcional)", required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}), help_text="Dejar en blanco o 0 si no tiene categoría.")
    # SIN __init__ personalizado aquí

class CategoryForm(forms.Form):
    name = forms.CharField(label="Nombre de la Categoría", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Smartphones, Laptops'}))
    description = forms.CharField(label="Descripción (Opcional)", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Una breve descripción de la categoría'}), required=False)