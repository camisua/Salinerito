from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_insumos, name='lista_insumos'),
    path('nuevo/', views.editar_insumo, name='nuevo_insumo'),
    path('<int:pk>/editar/', views.editar_insumo, name='editar_insumo'),
]
