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
from django.contrib.auth import get_user_model
User = get_user_model()





@login_required  # solo usuarios logueados pueden ver esto
def productos_bajo_stock(request):
    if not request.user.is_staff:
        return redirect('inicio')  # si no es admin, lo manda al inicio

    productos = Producto.objects.filter(stock__lte=5)  # stock bajo
    return render(request, 'tienda/bajo_stock.html', {'productos': productos})

# tienda/views.py (nuevo o editar inicio)
def inicio(request):
    qs = Producto.objects.all()
    q = request.GET.get('q')
    cat = request.GET.get('categoria')
    minp = request.GET.get('min_price')
    maxp = request.GET.get('max_price')

    if q:
        qs = qs.filter(nombre__icontains=q)
    if cat:
        qs = qs.filter(categoria__iexact=cat)

    try:
        minp_val = float(minp) if minp else None
        maxp_val = float(maxp) if maxp else None
    except ValueError:
        minp_val = maxp_val = None

    if minp_val is not None:
        qs = qs.filter(precio__gte=minp_val)
    if maxp_val is not None:
        qs = qs.filter(precio__lte=maxp_val)

    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    return render(request, 'tienda/inicio.html', {'productos': qs, 'categorias': categorias})






@login_required
def finalizar_compra(request):

    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('inicio')

    # Validar stock primero
    for item in carrito.values():
        producto = get_object_or_404(Producto, id=item['id'])
        if item['cantidad'] > producto.stock:
            messages.error(request, f"No hay suficientes unidades de {producto.nombre} (disponibles: {producto.stock}).")
            return redirect('ver_carrito')

    # Calcular total
    total = sum(item["precio"] * item["cantidad"] for item in carrito.values())

    # Crear orden
    orden = Orden.objects.create(usuario=request.user, total=total)

    cantidad_total = 0
    for item in carrito.values():
        producto = get_object_or_404(Producto, id=item["id"])

        # Crear OrdenItem
        OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=item["cantidad"]
        )

        # RESTAR stock y guardar
        producto.stock -= item["cantidad"]
        producto.save()

        cantidad_total += item["cantidad"]

    # Vaciar carrito
    request.session['carrito'] = {}

    # Notificar al admin (ver sección 6)
    from django.core.mail import send_mail
    try:
        send_mail(
            subject=f'Nueva orden #{orden.id}',
            message=f'Nueva orden #{orden.id} por {request.user.username}. Total: {orden.total}',
            from_email=None,                        # usa DEFAULT_FROM_EMAIL o None para backend dev
            recipient_list=[settings.DEFAULT_FROM_EMAIL],  # o admin list
            fail_silently=True,
        )
    except Exception:
        pass

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


from django.contrib import messages

@login_required
def agregar_al_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto = get_object_or_404(Producto, id=producto_id)

    # Cantidad actual en carrito
    cantidad_actual = carrito.get(str(producto_id), {}).get('cantidad', 0)

    # Si ya no hay stock disponible
    if cantidad_actual >= producto.stock:
        messages.error(request, "❌ No hay suficiente stock disponible.")
        return redirect('detalle_producto', producto_id=producto_id)

    # Si hay stock, añadir al carrito
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
    messages.success(request, "✔ Producto agregado al carrito.")

    # Redirigir a la misma página desde donde vino (preferible)
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))





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
    return render(request, "usuarios/login.html")


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


