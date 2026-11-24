from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('caja/', include('apps.caja.urls')),
    path('carta/', include('apps.carta.urls')),
    path('inventario/', include('apps.inventario.urls')),
    path('pedidos/', include('apps.pedidos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('', include('apps.usuarios.urls')),
]
