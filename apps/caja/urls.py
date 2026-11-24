from django.urls import path

from . import views

urlpatterns = [
    path('', views.por_cobrar, name='por_cobrar'),
    path('cobrar/<int:pk>/', views.cobrar, name='cobrar'),
    path('factura/<int:pk>/', views.ver_factura, name='ver_factura'),
    path('domicilios/', views.domicilios, name='domicilios'),
    path('cierre/', views.cierre, name='cierre_caja'),
]
