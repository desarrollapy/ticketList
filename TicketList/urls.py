"""TicketList URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from ticket import views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', views.login_page, name='login'),
    url(r'^main$', views.inicio, name='inicio'),
    url(r'^logout$', views.logout_page, name="logout"),
    # Navegacion para Roles.
    url(r'^rol/add', views.RoleAgregar),
    url(r'^rol/new', views.RoleNuevo, name="RolesNuevo"),
    url(r'^rol/todos', views.RolesList, name="RolesList"),
    url(r'^rol/editar/(?P<id>\d+)', views.RolesEditar, name="RolesEditar"),
    url(r'^rol/update/(?P<id>\d+)', views.RolesUpdate),
    url(r'^rol/detalle/(?P<id>\d+)', views.RolesDetalles, name="RolesEditar"),
    url(r'^rol/asignarPermisos/(?P<id>\d+)', views.RolesAsignarPermisos, name="RolesAsignar"),
    url(r'^rol/sacarPermiso/(?P<idGrupo>\d+)/(?P<idPermiso>\d+)', views.RolesSacarPermisos),
    # Navegacion de usuarios.
    url(r'^usuario/registrar', views.UserRegistrar, name="UsuarioRegistrar"),
    url(r'^usuario/listar', views.UserListar, name="UsuarioListar"),
    url(r'^usuario/detallar/(?P<id>\d+)', views.UserDetallar, name="UsuarioDetallar"),
    url(r'^usuario/actualizar/(?P<id>\d+)', views.UserActualizar, name="UsuarioDetallar"),
    url(r'^usuario/perfil', views.UserPerfil, name="UsuarioPerfil"),
    url(r'^usuario/CambiarPassword/(?P<id>\d+)', views.UserCambiarPassword, name="UsuarioCambiarPassword"),
    url(r'^usuario/primer-login', views.primerLogin, name="PrimerLogin"),

    # Navegacion de Tickets.
    url(r'^ticket/registrar', views.ticketAgregar, name="TicketRegistrar"),
    url(r'^ticket/guardar', views.ticketGuardar, name="TicketGuardar"),
    url(r'^ticket/detalle/(?P<id>\d+)', views.TicketDetallar, name="TicketDetalle"),
    url(r'^ticket/editar/(?P<id>\d+)', views.ticketEditar, name="TicketEditar"),
    url(r'^ticket/actualizar/(?P<id>\d+)', views.ticketActualizar, name="TicketActualizar"),
    url(r'^ticket/eliminar/(?P<id>\d+)', views.ticketEliminar, name="TicketEliminar"),

    url(r'^ticket/mis-tickets', views.ticketMisTickets, name="misTickets"),
    url(r'^ticket/pendientes', views.ticketPendientesList, name="TicketPendientes"),
    url(r'^ticket/atendidos', views.ticketAntendidosList, name="TicketAtendidos"),
    url(r'^ticket/solucionados', views.ticketSolucionadosList, name="TicketSolucionados"),
    url(r'^ticket/no-solucionados', views.ticketNoSolucionadosList, name="TicketNoSolucionados"),
    url(r'^ticket/atender/(?P<id>\d+)', views.ticketAtender, name="atenderTicket"),
    url(r'^ticket/solucionar/(?P<id>\d+)', views.ticketSolucionado, name="solucionarTicket"),

    url(r'^ticket/comentario/agregar/(?P<id>\d+)', views.ticketGuardarComentario, name="TicketGuardarComentario"),

    url(r'^ticket/sin-solucion/(?P<id>\d+)', views.ticketNoSolucionadoEdit, name="sinSolucionTicket"),
    url(r'^ticket/no-solucionar/(?P<id>\d+)', views.ticketNoSolucionar, name="noSolucionarTicket"),

    url(r'^ticket/actualizaciones-ajax/', views.ticketPushActualizaciones, name="TicketPush"),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)