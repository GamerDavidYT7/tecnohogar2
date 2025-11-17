from django.db import models
from django.contrib.auth.models import User
import uuid


# -----------------------
# MODELO PRODUCTO
# -----------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    imagen_principal = models.ImageField(upload_to="productos/")
    stock = models.PositiveIntegerField(default=0)  # 👈 NUEVO

    def __str__(self):
        return self.nombre



# -----------------------
# IMÁGENES MÚLTIPLES POR PRODUCTO
# -----------------------
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


# -----------------------
# RESEÑAS POR PRODUCTO
# -----------------------
class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="resenas")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    calificacion = models.IntegerField(default=5)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.usuario.username} - {self.calificacion}⭐"


# -----------------------
# ORDEN
# -----------------------
class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)   # NUEVO campo
    referencia_pago = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"

class Pago(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, default=uuid.uuid4)  # id simulado
    metodo = models.CharField(max_length=50, default='simulado')
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago {self.transaction_id} - {'OK' if self.aprobado else 'FALLA'}"


# -----------------------
# ITEMS DE LA ORDEN
# -----------------------
class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

