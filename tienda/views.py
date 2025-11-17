from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Producto, Orden, OrdenItem, Pago, Resena
import uuid
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@login_required
def finalizar_compra(request):

    carrito = request.session.get('carrito', {})

    if not carrito:
        return redirect('inicio')

    # Calcular total
    total = sum(item["precio"] * item["cantidad"] for item in carrito.values())

    # Crear orden
    orden = Orden.objects.create(
        usuario=request.user,
        total=total
    )

    cantidad_total = 0

    # Crear los items de la orden
    for item in carrito.values():
        OrdenItem.objects.create(
            orden=orden,
            producto_id=item["id"],
            cantidad=item["cantidad"]
        )
        cantidad_total += item["cantidad"]

    # Vaciar carrito
    request.session['carrito'] = {}

    # Mostrar página de compra exitosa
    return render(request, "tienda/compra_exitosa.html", {
        "orden": orden,
        "cantidad_total": cantidad_total
    })


# ---------------------------
# CARRITO Y ORDENES
# ---------------------------
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    for item in carrito.values():
        item["subtotal"] = item["precio"] * item["cantidad"]
    total = sum(item["subtotal"] for item in carrito.values())
    return render(request, 'tienda/carrito.html', {'carrito': carrito, 'total': total})


def agregar_al_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto = get_object_or_404(Producto, id=producto_id)
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': 1,
            'id': producto_id
        }
    request.session['carrito'] = carrito
    return redirect('inicio')


def vaciar_carrito(request):
    request.session['carrito'] = {}
    return redirect('ver_carrito')


def eliminar_item(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id = str(producto_id)
    if producto_id in carrito:
        if carrito[producto_id]['cantidad'] > 1:
            carrito[producto_id]['cantidad'] -= 1
        else:
            del carrito[producto_id]
    request.session['carrito'] = carrito
    return redirect('ver_carrito')


# ---------------------------
# USUARIO
# ---------------------------
def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {"form": form})


def iniciar_sesion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect("inicio")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "registration/login.html")


def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')


@login_required(login_url="/login/")
def perfil(request):
    usuario = request.user
    ordenes = Orden.objects.filter(usuario=usuario).order_by('-fecha')
    return render(request, "registration/perfil.html", {"usuario": usuario, "ordenes": ordenes})


@login_required(login_url="/login/")
def eliminar_cuenta(request):
    if request.method == "POST":
        usuario = request.user
        logout(request)
        usuario.delete()
        messages.success(request, "Tu cuenta ha sido eliminada correctamente.")
        return redirect("inicio")
    return render(request, "registration/eliminar_cuenta.html")


# ---------------------------
# DETALLE PRODUCTO
# ---------------------------
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "POST" and request.user.is_authenticated:
        Resena.objects.create(
            producto=producto,
            usuario=request.user,
            contenido=request.POST["contenido"],
            calificacion=request.POST["calificacion"]
        )
        return redirect("detalle_producto", producto_id=producto.id)
    resenas = producto.resenas.all()
    return render(request, "tienda/detalle_producto.html", {"producto": producto, "resenas": resenas})


# ---------------------------
# PAGO SIMULADO (opcional)
# ---------------------------
@login_required(login_url="/login/")
def pago_page(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    if orden.pagado:
        messages.info(request, "Esta orden ya fue pagada.")
        return redirect('inicio')
    return render(request, 'tienda/pago_page.html', {'orden': orden})


@login_required(login_url="/login/")
def procesar_pago(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    if request.method != 'POST':
        return redirect('pago_page', orden_id=orden.id)

    # Simulación de pago
    transaction_id = str(uuid.uuid4())
    pago = Pago.objects.create(
        orden=orden,
        monto=orden.total,
        transaction_id=transaction_id,
        metodo='simulado',
        aprobado=True
    )
    orden.pagado = True
    orden.referencia_pago = transaction_id
    orden.save()
    request.session['carrito'] = {}
    return render(request, 'tienda/pago_exitoso.html', {'orden': orden, 'pago': pago})


# ---------------------------
# INICIO
# ---------------------------
def inicio(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/inicio.html', {'productos': productos})


