from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_platos, name='lista_platos'),
    path('nuevo/', views.editar_plato, name='nuevo_plato'),
    path('<int:pk>/editar/', views.editar_plato, name='editar_plato'),
    path('<int:pk>/estado/', views.cambiar_estado_plato, name='estado_plato'),
]
