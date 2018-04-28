from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User, Permission
from django.core.exceptions import ValidationError
from django.shortcuts import render
from ticket.forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError  # Para manejar errores de la Base de Datos.import
from django.http import HttpResponseRedirect
from django.contrib import messages  # Para enviar mensajes de erorr al template.
import django.contrib.auth.password_validation as validators  # Para validar el password.

# Create your views here.


@login_required(login_url='/')
def inicio(request):
    return render(request, "dashboard.html",{});


def login_page(request):
    """
        Vista para ingresar y autenticarse, para poder utilizar el sistema.

    """
    if request.method == "POST":

        username = request.POST.get('usuario')
        password = request.POST.get('password')

        print(username)
        print(password)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/inicio')
            else:
                messages.add_message(request, messages.WARNING, 'User inactivo.')
        else:
            messages.add_message(request, messages.ERROR, 'Nombre de User y/o password incorrecto.')

    return render(request, 'login.html')


# CRUD: Roles
@login_required(login_url='/')
def RolesList(request, message=""):
    """
      Vistar para listar todos Roles en el sistema

    """

    currentUser = User.objects.get(id=request.user.id)

    if (currentUser.is_superuser):
        RolesList = Group.objects.all()
        return render(request,
                      'RolesList.html',
                      {'RolesList': RolesList,
                       'message': message
                       }
                      )
    else:
        data = {
            'error': 'ver roles'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def RoleNuevo(request):
    """
      Vista para agregar un nuevo Rol.

    """
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        form = GrupoForm()
        return render(request, 'RolesEdit.html', {'titulo': 'Crear Rol', 'form': form, 'action': '/rol/add/'})
    else:
        data = {
            'error': 'agregar roles'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def RoleAgregar(request):
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        form = GrupoForm(request.POST)
        if form.is_valid():
            nombreGrupo = request.POST['groupName']
            if Group.objects.filter(name__iexact=nombreGrupo):
                messages.add_message(request, messages.WARNING, 'Rol ya existe!')
                rol = Group(name=nombreGrupo)
                return render(request, 'RolesEdit.html', {'rol': rol, 'action': '/rol/add/', 'titulo': 'Crear Rol'})
            else:
                rol = Group.objects.create(name=nombreGrupo)
                rol.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Rol Agregado!')  # Debo cambiar que los mensajes aparezcan en listar

        return HttpResponseRedirect('/rol/todos')
    else:
        data = {
            'error': 'agregar roles'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def RolesEditar(request, id):
    """
      Vista para editar un Rol existente.

    """
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        rol = Group.objects.get(id=id)
        return render(request,
                      'RolesEdit.html',
                      {'action': '/rol/update/' + id,
                       'rol': rol,
                       'titulo': 'Modificar Rol'
                       }
                      )
    else:
        data = {
            'error': 'modificar roles'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def RolesUpdate(request, id):
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        rol = Group.objects.get(id=id)
        nuevoName = request.POST["groupName"]
        if nuevoName != rol.name:
            rol.name = nuevoName
            if Group.objects.filter(name__iexact=rol.name):
                messages.add_message(request, messages.SUCCESS,
                                     'El nombre del rol ya existe!')  # Se controla si el rol ya existe
                return render(request,
                              'RolesEdit.html',
                              {'action': '/rol/update/' + id,
                               'rol': rol,
                               'titulo': 'Modificar Rol',
                               })  # Cambie el tema del titulo en la pagina
            else:
                rol.save()
                messages.add_message(request, messages.SUCCESS, 'Rol Actualizado!')

        return HttpResponseRedirect('/rol/todos')
    else:
        data = {
            'error': 'modificar roles'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def RolesDetalles(request, id):
    """
      Vista para detallar un Rol existente.

    """
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        permisos = Permission.objects.all()
        rol = Group.objects.get(id=id)
        permGrupos = rol.permissions.all()
        # Se filtran los permisos que puede agregarse a un grupo
        listPermisos = []
        for obj in permisos:
            if not permGrupos.filter(codename__contains=obj.codename):
                listPermisos.append(obj)

        return render(request,
                      'RolesDetalles.html',
                      {'rol': rol,
                       'permGrupos': permGrupos,
                       'permisos': listPermisos}
                      )
    else:
        data = {
            'error': 'ver roles'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def RolesAsignarPermisos(request, id):
    """
      Vista para asginar permisos a un rol.

    """
    currentUser = User.objects.get(id=request.user.id)

    if (currentUser.is_superuser):
        listPermisos = request.POST.getlist('PermisosList')
        grupo = Group.objects.get(id=id)
        for obj in listPermisos:
            grupo.permissions.add(obj)
        return HttpResponseRedirect('/rol/detalle/' + id)
    else:
        data = {
            'error': 'asignar permisos a roles'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def RolesSacarPermisos(request, idPermiso, idGrupo):
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        grupo = Group.objects.get(id=idGrupo)
        permiso = Permission.objects.get(id=idPermiso)
        grupo.permissions.remove(permiso)

        return HttpResponseRedirect('/rol/detalle/' + idGrupo)
    else:
        data = {
            'error': 'sacar permisos a roles'
        }
        return render(request, 'sinPermisos.html', data)
    
# CRUD: User
@login_required(login_url='/')
def UserNuevo(request):
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):

        form = RegistrarUserForm()
        context = {
            'form': form,
            'action': '/User/registrar/'

        }
        return render(request, 'UserRegistrar.html', context)
    else:
        data = {
            'error': 'crear Users',
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def UserRegistrar(request, *kwargs):
    """
        Vista para registrar un nuevo User.

    """
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        if request.method == "POST":
            form = RegistrarUserForm(request.POST)
            if form.is_valid():
                Email = form.cleaned_data['Email'].lower()
                Username = form.cleaned_data['Usuario']
                Password = form.cleaned_data['Password']
                Nombre = form.cleaned_data['Nombre']
                Apellido = form.cleaned_data['Apellido']
                Administrador = form.cleaned_data['Administrador']
                Estado = form.cleaned_data['Estado']

            try:

                validators.validate_password(Password)
                UserNuevo = User.objects.create_user(email=Email, username=Username, password=Password,
                                                           first_name=Nombre,
                                                           last_name=Apellido,
                                                           is_superuser=Administrador, is_active=Estado)

                UserNuevo.save()
                messages.add_message(request, messages.SUCCESS, 'User registrado.')
                return render(request, 'UserRegistrar.html')

            except IntegrityError:

                UserNuevo = User(email=Email, username=Username, password=Password,
                                       nombre=Nombre,
                                       apellido=Apellido,
                                       is_superuser=Administrador, is_active=Estado)
                context = {
                    'User': UserNuevo,
                }

                messages.add_message(request, messages.ERROR, 'User existente.')
                return render(request, 'UserRegistrar.html', context)

            except ValidationError:
                UserNuevo = User(email=Email, username=Username, password=Password,
                                       nombre=Nombre,
                                       apellido=Apellido,
                                       is_superuser=Administrador, is_active=Estado)
                context = {
                    'User': UserNuevo,
                }

                messages.add_message(request, messages.ERROR,
                                     'Password inseguro, utilice al menos 8 caracteres alfanumericos.')
                return render(request, 'UserRegistrar.html', context)

        return render(request, 'UserRegistrar.html')
    else:
        data = {
            'error': 'crear User'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def UserListar(request):
    """
        Vista para listar los Users registrados.

    """
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        usuariosRegistrados = User.objects.all()

        context = {
            'usuariosRegistrados': usuariosRegistrados,
        }

        return render(request, 'UserListar.html', context)
    else:
        data = {
            'error': 'listar Users'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def UserDetallar(request, id):
    """
        Vista para detallar un User registrado.

    """
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):
        UserRegistrado = User.objects.get(id=id)
        context = {'Email': UserRegistrado.email,
                   'User': UserRegistrado.username,
                   'Password': UserRegistrado.password,
                   'Nombre': UserRegistrado.nombre,
                   'Apellido': UserRegistrado.apellido,
                   'Administrador': UserRegistrado.is_superuser,
                   'Estado': UserRegistrado.is_active,
                   'ID': UserRegistrado.id,
                   'action': '/User/actualizar/' + id,
                   'titulo': 'Modificar'
                   }

        return render(request, 'UserDetallar.html', context)
    else:
        data = {
            'error': 'detallar Users'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def UserActualizar(request, id):
    """
        Vista para actualizar un User registrado.

    """
    currentUser = User.objects.get(id=request.user.id)
    if (currentUser.is_superuser):

        UserRegistrado = User.objects.get(id=id)

        if request.method == "POST":
            form = RegistrarUserForm(request.POST)
            print form.errors
            if form.is_valid():
                UserRegistrado.email = form.cleaned_data['Email'].lower()
                UserRegistrado.username = form.cleaned_data['User'].lower()
                UserRegistrado.nombre = form.cleaned_data['Nombre']
                UserRegistrado.apellido = form.cleaned_data['Apellido']
                UserRegistrado.is_superuser = form.cleaned_data['Administrador']
                UserRegistrado.is_active = form.cleaned_data['Estado']

            try:

                UserRegistrado.save()

                messages.add_message(request, messages.SUCCESS, 'User modificado.')
                context = {'Email': UserRegistrado.email,
                           'User': UserRegistrado.username,
                           'Nombre': UserRegistrado.nombre,
                           'Apellido': UserRegistrado.apellido,
                           'Administrador': UserRegistrado.is_superuser,
                           'Estado': UserRegistrado.is_active,
                           }

                return render(request, 'UserDetallar.html', context)

            except IntegrityError:
                messages.add_message(request, messages.ERROR, 'User existente.')

        context = {'Email': UserRegistrado.email,
                   'User': UserRegistrado.username,
                   'Nombre': UserRegistrado.nombre,
                   'Apellido': UserRegistrado.apellido,
                   'Administrador': UserRegistrado.is_superuser,
                   'Estado': UserRegistrado.is_active,
                   }

        return render(request, 'UserDetallar.html', context)
    else:
        data = {
            'error': 'modificar Users'
        }
        return render(request, 'sinPermisos.html', data)


@login_required(login_url='/')
def UserPerfil(request):
    """
        Vista para visualizar el perfil de un User registrado.

    """
    UserRegistrado = request.user
    id = UserRegistrado.id

    context = {'Email': UserRegistrado.email,
               'User': UserRegistrado.username,
               'Password': UserRegistrado.password,
               'Nombre': UserRegistrado.nombre,
               'Apellido': UserRegistrado.apellido,
               'Administrador': UserRegistrado.is_superuser,
               'Estado': UserRegistrado.is_active,
               'ID': UserRegistrado.id,
               'action': '/User/actualizar/' + str(id),
               'titulo': 'Mi Perfil'
               }

    return render(request, 'UserDetallar.html', context)


@login_required(login_url='/')
def UserCambiarPassword(request, id):
    """
        Vista para realizar un cambio de password.

    """

    UserRegistrado = User.objects.get(id=id)
    PasswordGuardado = UserRegistrado.password

    if request.method == "POST":
        PasswordAnterior = request.POST['PasswordAnterior']
        PasswordNuevo = request.POST['PasswordNuevo']
        PasswordRepetido = request.POST['PasswordRepetido']

        if check_password(PasswordAnterior, PasswordGuardado) and PasswordNuevo == PasswordRepetido:

            try:

                validators.validate_password(PasswordNuevo)
                UserRegistrado.set_password(PasswordNuevo)

                UserRegistrado.save()

                messages.add_message(request, messages.SUCCESS, 'Password modificado.')

                return render(request, 'UserCambiarPassword.html')

            except ValidationError:
                messages.add_message(request, messages.ERROR,
                                     'Password inseguro, utilice al menos 8 caracteres alfanumericos.')
                return render(request, 'UserCambiarPassword.html')

        else:
            messages.add_message(request, messages.SUCCESS, 'No coinciden los passwords.')

    context = {'id': id}
    return render(request, 'UserCambiarPassword.html', context)
