from django.urls import path

from . import views

urlpatterns = [
    path('mesas/', views.mesas, name='mesas'),
    path('nuevo/', views.nuevo_pedido, name='nuevo_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('<int:pk>/estado/', views.estado_pedido, name='estado_pedido'),
    path('cocina/', views.cocina, name='cocina'),
]
