from django.urls import path
from . import views

urlpatterns = [
    # Usuario
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('eliminar_cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path("perfil/", views.perfil, name="perfil"),

    # Tienda
    path('', views.inicio, name='inicio'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path("carrito/eliminar/<int:producto_id>/", views.eliminar_item, name="eliminar_item"),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # FINALIZAR COMPRA (nuevo)
    path('finalizar_compra/', views.finalizar_compra, name='finalizar_compra'),

    # Pago simulado (lo puedes borrar si ya no lo usarás)
    path('pago/<int:orden_id>/', views.pago_page, name='pago_page'),
    path('procesar_pago/<int:orden_id>/', views.procesar_pago, name='procesar_pago'),
]





