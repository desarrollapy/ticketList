from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User, Permission
from django.core.exceptions import ValidationError
from django.shortcuts import render
from ticket.forms import *
from ticket.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError  # Para manejar errores de la Base de Datos.import
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages  # Para enviar mensajes de erorr al template.
from django.core import  serializers
import django.contrib.auth.password_validation as validators  # Para validar el password.
import datetime

# Create your views here.

@login_required(login_url='/')
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url='/')
def inicio(request):
    currentUser = User.objects.get(id=request.user.id)
    persona = Persona.objects.filter(usuario=currentUser)
    if(persona.first().first_login == True):
        for obj in currentUser.groups.all():
            if(obj.id == 1):
                return HttpResponseRedirect('/ticket/mis-tickets')

        pendientes = Ticket.objects.filter(estado='PENDIENTE').count()
        atendidos = Ticket.objects.filter(estado='ATENDIDO').count()
        solucionados = Ticket.objects.filter(estado='SOLUCIONADO').count()
        nosolucionados = Ticket.objects.filter(estado='NO_SOLUCIONADO').count()

        topTickets = Ticket.objects.all().order_by('-fechaModificacion')[:10]

        return render(request, "dashboard.html",
                      {
                          "pendientes":pendientes,
                          "atendidos":atendidos,
                          "solucionados":solucionados,
                          "nosolucionados":nosolucionados,
                          "topTickets":topTickets,
                      });
    else:
        return HttpResponseRedirect('/usuario/primer-login')


def login_page(request):
    """
        Vista para ingresar y autenticarse, para poder utilizar el sistema.

    """
    if request.method == "POST":

        username = request.POST.get('usuario')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/main')
            else:
                messages.add_message(request, messages.WARNING, 'User inactivo.')
        else:
            messages.add_message(request, messages.ERROR, 'Nombre de User y/o password incorrecto.')

    return render(request, 'login.html')

@login_required(login_url='/')
def primerLogin(request):
    currentUser = User.objects.get(id=request.user.id)
    if request.method == "POST":
        passwordnuevo = request.POST.get('passwordnuevo')
        againpassword = request.POST.get('againpassword')
        if passwordnuevo == againpassword:
            validators.validate_password(passwordnuevo)
            currentUser.set_password(passwordnuevo)
            currentUser.save()

            persona = Persona.objects.filter(usuario=currentUser).first()
            persona.first_login = True;
            persona.save()
            messages.add_message(request, messages.SUCCESS, 'Password modificado.')
            user = authenticate(username=currentUser.username, password=passwordnuevo)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/main')
        else:
            messages.add_message(request, messages.ERROR, 'Las contrase;as no coinciden')
    return render(request, 'changePassword.html', {"action":"/usuario/primer-login"})

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
                againPassword = form.cleaned_data['againPassword']
                codigo = form.cleaned_data['codigo']
                Nombre = form.cleaned_data['Nombre']
                Apellido = form.cleaned_data['Apellido']
                Administrador = form.cleaned_data['Administrador']
                Estado = form.cleaned_data['Estado']
                rol = Group.objects.get(id=request.POST['rol'])
            try:
                if(Password == againPassword):
                    validators.validate_password(Password)
                    UserNuevo = User.objects.create_user(email=Email, username=Username, password=Password,
                                                         first_name=Nombre,
                                                         last_name=Apellido,
                                                         is_superuser=Administrador,
                                                         is_active=Estado,
                                                         is_staff=True)
                    UserNuevo.groups.add(rol);
                    UserNuevo.save()
                    persona = Persona(first_login=False, codigo = codigo, usuario=UserNuevo)
                    persona.save()

                    messages.add_message(request, messages.SUCCESS, 'User registrado.')
                    return render(request, 'UserRegistrar.html')
                else:
                    UserNuevo = User(email=Email, username=Username, password=Password,
                                     first_name=Nombre,
                                     last_name=Apellido,
                                     is_superuser=Administrador, is_active=Estado)
                    roles = Group.objects.all()

                    context = {
                        'usuario': UserNuevo,
                        'roles': roles,
                        'action': '/usuario/registrar/'
                    }

                    messages.add_message(request, messages.ERROR, 'Las contrase&ntilde;as no coinciden.')
                    return render(request, 'UserRegistrar.html', context)


            except IntegrityError:

                UserNuevo = User(email=Email, username=Username, password=Password,
                                 first_name=Nombre,
                                 last_name=Apellido,
                                       is_superuser=Administrador, is_active=Estado)
                roles = Group.objects.all()

                context = {
                    'usuario': UserNuevo,
                    'roles': roles,
                    'action': '/usuario/registrar/'
                }

                messages.add_message(request, messages.ERROR, 'User existente.')
                return render(request, 'UserRegistrar.html', context)

            except ValidationError:
                UserNuevo = User(email=Email, username=Username, password=Password,
                                 first_name=Nombre,
                                 last_name=Apellido,
                                       is_superuser=Administrador, is_active=Estado)
                roles = Group.objects.all()

                context = {
                    'usuario': UserNuevo,
                    'roles': roles,
                    'action': '/usuario/registrar/'
                }

                messages.add_message(request, messages.ERROR,
                                     'Password inseguro, utilice al menos 8 caracteres alfanumericos.')
                return render(request, 'UserRegistrar.html', context)

        roles = Group.objects.all()

        context = {
            'roles': roles,
            'action': '/usuario/registrar/'
        }
        return render(request, 'UserRegistrar.html', context)
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
        roles = Group.objects.all()
        rolRegistrado = UserRegistrado.groups.all()
        persona = Persona.objects.filter(usuario=UserRegistrado)
        persona = persona.first();
        if(rolRegistrado.count() > 0 ):
            rolRegistrado = rolRegistrado[0]
        else :
            rolRegistrado = {}

        context = {'usuario': UserRegistrado,
                   'ID': UserRegistrado.id,
                   'action': '/usuario/actualizar/' + id,
                   'titulo': 'Modificar',
                   'persona':persona,
                   'roles':roles,
                   'rolRegistrado': rolRegistrado,
                   }

        return render(request, 'UserRegistrar.html', context)
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
        persona = Persona.objects.filter(usuario=UserRegistrado)
        persona = persona.first();
        if request.method == "POST":
            form = RegistrarUserForm(request.POST)
            print form.errors
            UserRegistrado.email = form.cleaned_data['Email'].lower()
            UserRegistrado.username = form.cleaned_data['Usuario'].lower()
            UserRegistrado.nombre = form.cleaned_data['Nombre']
            UserRegistrado.apellido = form.cleaned_data['Apellido']
            UserRegistrado.is_superuser = form.cleaned_data['Administrador']
            UserRegistrado.is_active = form.cleaned_data['Estado']
            persona.codigo = form.cleaned_data['codigo']

            UserRegistrado.groups.clear()
            rol = Group.objects.get(id=request.POST['rol'])
            UserRegistrado.groups.add(rol)

            try:

                UserRegistrado.save()
                persona.save();
                messages.add_message(request, messages.SUCCESS, 'User modificado.')
                return HttpResponseRedirect('/usuario/detallar/' + id)
                # return render(request, 'UserDetallar.html', context)

            except IntegrityError:
                messages.add_message(request, messages.ERROR, 'User existente.')

        context = {'Email': UserRegistrado.email,
                   'User': UserRegistrado.username,
                   'Nombre': UserRegistrado.nombre,
                   'Apellido': UserRegistrado.apellido,
                   'Administrador': UserRegistrado.is_superuser,
                   'Estado': UserRegistrado.is_active,
                   }
        return HttpResponseRedirect('/usuario/detallar/' + id)
        # return render(request, 'UserDetallar.html', context)
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
    usuario = User.objects.get(id=request.user.id)
    persona = Persona.objects.filter(usuario=usuario)
    persona = persona.first()
    context = {
        'usuario': usuario,
        'persona': persona,
        }

    return render(request, 'UserPerfil.html', context)


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
            messages.add_message(request, messages.WARNING, 'No coinciden los passwords.')

    context = {'id': id}
    return render(request, 'UserCambiarPassword.html', context)

@login_required(login_url='/')
@permission_required('ticket.add_ticket', raise_exception=True)
def ticketAgregar(request):
    """
        Vista para agregar un Ticket.
    """
    inconvenientes = Inconveniente.objects.all()
    data = {
        'inconvenientes': inconvenientes,
        'titulo': 'Crear Ticket',
        'action': '/ticket/guardar',
    }

    return render(request, 'TicketEdit.html', data)

@login_required(login_url='/')
@permission_required('ticket.add_ticket', raise_exception=True)
def ticketEditar(request, id):
    """
        Vista para agregar un Ticket.
    """
    ticket = Ticket.objects.get(id=id)
    inconvenientes = Inconveniente.objects.all()
    data = {
        'ticket':ticket,
        'inconvenientes': inconvenientes,
        'titulo': 'Modificar Ticket',
        'action': '/ticket/actualizar/' + id,
    }

    return render(request, 'TicketEdit.html', data)


@login_required(login_url='/')
@permission_required('ticket.add_ticket', raise_exception=True)
def ticketGuardar(request):
    """
        Vista para guardar un ticket.
    """
    if request.method == 'POST':
        usuario = User.objects.get(id=request.user.id)
        persona = Persona.objects.filter(usuario = usuario)
        codigo = persona.first().codigo
        descripcion = request.POST['descripcion']
        numero = request.POST['numero']
        shelter = request.POST['shelter']
        inconveniente = Inconveniente.objects.get(id=request.POST['inconveniente'])
        central = Central.objects.get(id=1)
        ticket = Ticket(
            descripcionBreve= descripcion,
            shelter= shelter,
            inconveniente = inconveniente,
            central = central,
            usuarioCreacion = usuario,
            usuarioEncargado = usuario,
            estado = 'PENDIENTE',
            numeroAfectado=numero,
            codigo=codigo,
        )
        ticket.save()
        messages.add_message(request, messages.SUCCESS, 'Ticket Creado')
        return HttpResponseRedirect('/ticket/mis-tickets')

@login_required(login_url='/')
@permission_required('ticket.add_ticket', raise_exception=True)
def ticketActualizar(request, id):
    """
        Vista para guardar un ticket.
    """
    if request.method == 'POST':
        ticket = Ticket.objects.get(id=id)
        ticket.descripcionBreve = request.POST['descripcion']
        ticket.shelter = request.POST['shelter']
        inconveniente = Inconveniente.objects.get(id=request.POST['inconveniente'])
        ticket.inconveniente = inconveniente
        central = Central.objects.get(id=1)
        ticket.save()
        messages.add_message(request, messages.SUCCESS, 'Ticket Actualizado')
        return HttpResponseRedirect('/ticket/detalle/' + id)

@login_required(login_url='/')
@permission_required('ticket.delete_ticket', raise_exception=True)
def ticketEliminar(request, id):
    """
        Vista para guardar un ticket.
    """

    ticket = Ticket.objects.get(id=id)
    comentarios = Comentarios.objects.filter(ticket = ticket)
    for comt in comentarios :
        comt.delete()
    ticket.delete()
    messages.add_message(request, messages.SUCCESS, 'Ticket Borrado!')
    return HttpResponseRedirect('/ticket/mis-tickets')


@login_required(login_url='/')
@permission_required('ticket.view_ticket', raise_exception=True)
def TicketDetallar(request, id):
    """
        Vista para detallar un User registrado.

    """
    ticket = Ticket.objects.get(id=id)
    comentarios = Comentarios.objects.filter(ticket = ticket)
    context = {
        'ticket': ticket,
        'comentarios': comentarios,
        'actionComentar': '/ticket/comentario/agregar/' + id
    }
    return render(request, 'TicketDetalle.html', context)

@login_required(login_url='/')
@permission_required('ticket.add_ticket', raise_exception=True)
def ticketGuardarComentario(request, id):
    """
        Vista para guardar un ticket.
    """
    if request.method == 'POST':
        usuario = User.objects.get(id=request.user.id)
        comentario = request.POST['comentario']
        ticket = Ticket.objects.get(id=id)
        comentario = Comentarios(
            comentario= comentario,
            autor= usuario,
            ticket = ticket,
            lado = 1
        )
        comentario.save()
        messages.add_message(request, messages.SUCCESS, 'Comentario agregado')
        return HttpResponseRedirect('/ticket/detalle/' + id)

@login_required(login_url='/')
@permission_required('ticket.view_ticket', raise_exception=True)
def ticketPendientesList(request):
    ticketList = Ticket.objects.all().filter(estado__exact='PENDIENTE')
    return render(request, "TicketList.html",{
        "ticketList":ticketList,
        "titulo":"Tickets Pendientes",
        "pagina":"PENDIENTE"
    });

@login_required(login_url='/')
@permission_required('ticket.view_ticket', raise_exception=True)
def ticketAntendidosList(request):
    ticketList = Ticket.objects.all().filter(estado__exact='ATENDIDO')
    return render(request, "TicketList.html",{
        "ticketList":ticketList,
        "titulo":"Tickets Atendidos",
        "pagina": "ATENDIDO"
    });

@login_required(login_url='/')
@permission_required('ticket.view_ticket', raise_exception=True)
def ticketSolucionadosList(request):
    ticketList = Ticket.objects.all().filter(estado__exact='SOLUCIONADO')
    return render(request, "TicketList.html",{
        "ticketList":ticketList,
        "titulo":"Tickets Solucionados",
        "pagina": "SOLUCIONADO"
    });

@login_required(login_url='/')
@permission_required('ticket.view_ticket', raise_exception=True)
def ticketNoSolucionadosList(request):
    ticketList = Ticket.objects.all().filter(estado__exact='NO_SOLUCIONADO')
    return render(request, "TicketList.html",{
        "ticketList":ticketList,
        "titulo":"Tickets No Solucionados",
        "pagina": "NO_SOLUCIONADO"
    });

@login_required(login_url='/')
@permission_required('ticket.change_state_ticket', raise_exception=True)
def ticketAtender(request, id):
    usuario = User.objects.get(id=request.user.id);
    ticket = Ticket.objects.get(id=id)
    ticket.estado = 'ATENDIDO'
    ticket.fechaAtencion = datetime.datetime.now()
    ticket.usuarioEncargado = usuario
    ticket.save()
    messages.add_message(request, messages.SUCCESS, 'Ticket marcado como atendido')
    return HttpResponseRedirect('/ticket/pendientes')

@login_required(login_url='/')
@permission_required('ticket.change_state_ticket', raise_exception=True)
def ticketSolucionado(request, id):
    usuario = User.objects.get(id=request.user.id);
    ticket = Ticket.objects.get(id=id)
    if usuario.id == ticket.usuarioEncargado.id:
        ticket.estado = 'SOLUCIONADO'
        ticket.save()
        ticket.fechaCierre = datetime.datetime.now()
        messages.add_message(request, messages.SUCCESS, 'Ticket marcado como solucionado')
        return HttpResponseRedirect('/ticket/atendidos')
    else:
        messages.add_message(request, messages.ERROR, 'No esta autorizado a solucionar ticket')
        return HttpResponseRedirect('/ticket/atendidos')


@login_required(login_url='/')
@permission_required('ticket.change_state_ticket', raise_exception=True)
def ticketNoSolucionadoEdit(request, id):
    usuario = User.objects.get(id=request.user.id);
    ticket = Ticket.objects.get(id=id)
    if usuario.id == ticket.usuarioEncargado.id:
        motivos = Motivo.objects.all();
        action = "/ticket/no-solucionar/" + str(id)
        context = {
            "motivosList":motivos,
            "action":action,
        }
        return render(request, 'TicketNoSolucionadoEdit.html', context)
    else:
        messages.add_message(request, messages.ERROR, 'No esta autorizado a solucionar ticket')
        return HttpResponseRedirect('/ticket/atendidos')

@login_required(login_url='/')
@permission_required('ticket.change_state_ticket', raise_exception=True)
def ticketNoSolucionar(request, id):
    usuario = User.objects.get(id=request.user.id);
    ticket = Ticket.objects.get(id=id)
    if usuario.id == ticket.usuarioEncargado.id:
        if request.method == 'POST':
            motivo = Motivo.objects.get(id=request.POST['motivo'])
            ticket.motivo = motivo
            ticket.estado = "NO_SOLUCIONADO"
            ticket.fechaCierre = datetime.datetime.now()
            ticket.save()
            messages.add_message(request, messages.SUCCESS, 'Ticket marcado como No solucionado')
            return HttpResponseRedirect('/ticket/atendidos')

    else:
        messages.add_message(request, messages.ERROR, 'No esta autorizado a solucionar ticket')
        return HttpResponseRedirect('/ticket/atendidos')

@login_required(login_url='/')
def ticketMisTickets(request):
    usuario = User.objects.get(id=request.user.id)
    ticketList = Ticket.objects.all().filter(usuarioCreacion=usuario)
    return render(request, "TicketList.html",{
        "ticketList":ticketList,
        "titulo":"Mis Tickets",
        "pagina":"MISTICKETS"
    });

@login_required(login_url='/')
def ticketPushActualizaciones(request):
    usuario = User.objects.get(id=request.user.id)
    pagina = request.GET.get('estado')
    ticketList = Ticket.objects.all().filter(estado__exact=pagina)
    data = serializers.serialize('json', ticketList)
    return HttpResponse(data, content_type='application/json')



@login_required(login_url='/')
def centralesList(request):
    centrales = Central.objects.all();
    return render(request, "CentralList.html", {
        "centralList":centrales,
    })

