from django.urls import path

from . import views

urlpatterns = [
    path('panel/', views.panel, name='panel'),
    path('', views.reportes, name='reportes'),
    path('csv/', views.exportar_csv, name='reportes_csv'),
]
