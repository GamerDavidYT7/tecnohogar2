from django.contrib import admin
from .models import Producto
# tienda/admin.py
from .models import Producto, Orden, OrdenItem, Resena, ImagenProducto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)

admin.site.register(ImagenProducto)
admin.site.register(Resena)
admin.site.register(Orden)
admin.site.register(OrdenItem)
