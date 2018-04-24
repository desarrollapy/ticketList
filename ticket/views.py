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
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    print "Entrooo"
                    return HttpResponseRedirect('/inicio')
                else:
                    print "Usuario inactivo."
                    messages.add_message(request, messages.WARNING, 'Usuario inactivo.')
            else:
                print "Nombre de usuario y/o password incorrecto."
                messages.add_message(request, messages.ERROR, 'Nombre de usuario y/o password incorrecto.')
        else:
            messages.add_message(request, messages.WARNING, 'Datos invalidos.')
    else:
        form = LoginForm()

    return render(request, 'login.html')