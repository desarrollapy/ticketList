from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Central(models.Model):
    descripcion = models.CharField(max_length=64)

class Inconveniente(models.Model):
    descripcion = models.CharField(max_length=20)

class Motivo(models.Model):
    descripcion = models.CharField(max_length=64)

class Ticket(models.Model):
    """
        Se encarga de manejar las plantillas (tipos) para los user stories.

        :param descripcionBreve: Char Field
        :param comentario: Text Field
    """
    descripcionBreve = models.TextField()
    shelter = models.CharField(max_length=128)
    inconveniente = models.ForeignKey(Inconveniente, null=False, on_delete=models.CASCADE)
    motivo = models.ForeignKey(Motivo, null=True, on_delete=models.CASCADE)
    central = models.ForeignKey(Central, null=False, on_delete=models.CASCADE)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaAtencion = models.DateTimeField(null=True, db_column='fecha_atencion');
    fechaCierre = models.DateTimeField(null=True, db_column='fecha_cierre');
    usuarioCreacion = models.ForeignKey(User, related_name='usuario_creacion')
    usuarioEncargado = models.ForeignKey(User, related_name='usuario_encargado')
    estado = models.CharField(max_length=64)
    codigo = models.CharField(max_length=128, null=True)
    numeroAfectado = models.CharField(max_length=128, db_column='numero_afectado', null=True)

    class Meta:
        permissions = (
            ('change_state_ticket', 'Puede cambiar estado del ticket'),
            ('view_ticket', 'Puede listar los ticket'),
            ('view_pendientes_ticket', 'Puede listar los ticket pendientes'),
            ('view_atendidos_ticket', 'Puede listar los ticket atendidos'),
            ('view_solucionados_ticket', 'Puede listar los ticket solucionados'),
            ('view_no_solucionados_ticket', 'Puede listar los ticket no solucionados'),
        )

class Comentarios(models.Model):
    """
        Se encarga de manejar los comentarios de un user story.
        :param autor: Foreign Key Usuario
        :param titulo: Char Field
        :param comentario: Text Field
        :param fechaComentario: DateTime Field
        :param userStory: Foreign Key userStory
        :param lado: Integer Field
    """

    autor = models.ForeignKey(User)
    comentario = models.TextField()
    fechaComentario = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket, null=True)
    lado = models.IntegerField()

class Persona(models.Model):
    usuario = models.ForeignKey(User)
    codigo = models.CharField(max_length=128)
    first_login = models.BooleanField(default=False)