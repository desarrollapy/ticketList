from django import forms

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput())

class GrupoForm(forms.Form):
    groupName = forms.CharField(required=True,label='Nombre Rol',error_messages={'required': "El Rol ingresado no es valido, ingrese nuevamente"})

class RegistrarUserForm(forms.Form):
    Email = forms.EmailField(error_messages={'required':'Ingrese una direccion de correo con valida'},required=True)
    Usuario = forms.CharField(max_length=40,error_messages={'required':'Por favor ingrese un nombre de usuario valido'},required=True)
    Password = forms.CharField(widget=forms.PasswordInput(),error_messages={'required':'Ingrese un password valido'}, required=False)
    Nombre = forms.CharField(max_length=100,error_messages={'required':'Debe ingresar un Nombre para su perfil'},required=True)
    Apellido = forms.CharField(max_length=100,error_messages={'required':'Debe ingresar un Apellido para su perfil'},required=True)
    Administrador = forms.BooleanField(initial=False, required=False,error_messages={'required':'Indique si es administrador'})
    Estado = forms.BooleanField(initial=True,required=False,error_messages={'required':'Indique su Estado'})
