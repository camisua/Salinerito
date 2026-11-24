from django.urls import path

from . import views

urlpatterns = [
    path('platos/', views.PlatoListAPI.as_view(), name='api_platos'),
    path('pedidos/', views.PedidoListCreateAPI.as_view(), name='api_pedidos'),
    path('pedidos/<int:pk>/estado/', views.CambiarEstadoAPI.as_view(), name='api_estado_pedido'),
    path('cocina/', views.CocinaAPI.as_view(), name='api_cocina'),
    path('insumos/alertas/', views.InsumoAlertasAPI.as_view(), name='api_alertas'),
]
