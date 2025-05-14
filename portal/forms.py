# scl_frontend_django/portal/forms.py

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nombre de Usuario",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre de usuario'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Tu contraseña'})
    )

    # Opcional: Añadir un campo "Recordarme" si quisieras implementar esa lógica
    # remember_me = forms.BooleanField(label="Recordarme", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Podrías añadir más personalizaciones aquí si fuera necesario
        # Por ejemplo, para los placeholders o clases CSS de forma más dinámica.