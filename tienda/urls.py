from django.urls import path
from . import views

urlpatterns = [
    # Sesión
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('eliminar_cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),

    # Tienda
    path('', views.inicio, name='inicio'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path("carrito/eliminar/<int:producto_id>/", views.eliminar_item, name="eliminar_item"),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/bajo-stock/', views.productos_bajo_stock, name='bajo_stock'),

    # Compra
    path('finalizar_compra/', views.finalizar_compra, name='finalizar_compra'),
    path('pago/<int:orden_id>/', views.pago_page, name='pago_page'),
    path('procesar_pago/<int:orden_id>/', views.procesar_pago, name='procesar_pago'),
]
