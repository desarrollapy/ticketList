from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ticket.forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages  # Para enviar mensajes de erorr al template.
# Create your views here.


@login_required(login_url='/')
def inicio(request):
    return render(request, "base.html",{});


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
                messages.add_message(request, messages.WARNING, 'Usuario inactivo.')
        else:
            messages.add_message(request, messages.ERROR, 'Nombre de usuario y/o password incorrecto.')

    return render(request, 'login.html')