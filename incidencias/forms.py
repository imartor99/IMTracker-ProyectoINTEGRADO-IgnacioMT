from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Incidencia, Observacion

# Formulario de login
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'id': 'Usuario',
            'maxlength': '32',
            'required': True,
            'name': 'usuario'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '******',
            'required': True,
            'name': 'contra'
        })
    )



# Formulario de creación y edición de incidencias
class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['titulo', 'descripcion', 'prioridad', 'imagen']

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen and imagen.size > 5*1024*1024:
            raise forms.ValidationError("La imagen no puede superar los 5MB.")
        return imagen


# Formulario para actualizar estado (IT)
class EstadoIncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['estado']


# Formulario para añadir observaciones obligatorias
class ObservacionForm(forms.ModelForm):
    class Meta:
        model = Observacion
        fields = ['texto']
