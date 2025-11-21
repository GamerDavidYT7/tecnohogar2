# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model

Usuario = get_user_model()

def login_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect("inicio")  # TE ENVÍA A LA PÁGINA PRINCIPAL
        else:
            return render(request, "usuarios/login.html", {"error": "Credenciales incorrectas"})

    return render(request, "usuarios/login.html")


def registro(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if Usuario.objects.filter(email=email).exists():
            return render(request, "usuarios/registro.html", {"error": "El email ya está registrado"})

        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("inicio")

    return render(request, "usuarios/registro.html")
