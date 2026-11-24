from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carta.models import Plato
from apps.inventario.models import Insumo
from apps.pedidos import servicios
from apps.pedidos.models import Pedido

from .permissions import RolPermitido
from .serializers import (CrearPedidoSerializer, EstadoSerializer, InsumoAlertaSerializer,
                          PedidoSerializer, PlatoSerializer)

TODOS = ['ADMINISTRADOR', 'MESERO', 'COCINA', 'CAJERO']

# Qué estados puede poner cada rol
ESTADOS_POR_ROL = {
    'COCINA': {'EN_PREPARACION', 'LISTO', 'ENTREGADO'},
    'MESERO': {'ENTREGADO', 'CANCELADO'},
    'ADMINISTRADOR': {'EN_PREPARACION', 'LISTO', 'ENTREGADO', 'CANCELADO'},
}


def _pedidos():
    return Pedido.objects.select_related('mesa', 'mesero', 'domicilio') \
        .prefetch_related('detalles__plato')


class PlatoListAPI(generics.ListAPIView):
    """GET /api/platos/ → carta disponible."""
    permission_classes = [RolPermitido]
    roles = TODOS
    serializer_class = PlatoSerializer
    queryset = Plato.objects.filter(activo=True).select_related('categoria')


class PedidoListCreateAPI(APIView):
    """GET /api/pedidos/ → pedidos de hoy.   POST /api/pedidos/ → crear pedido."""
    permission_classes = [RolPermitido]
    roles = ['ADMINISTRADOR', 'MESERO']

    def get(self, request):
        inicio, fin = servicios.rango_de_hoy()
        pedidos = _pedidos().filter(fecha_creacion__gte=inicio, fecha_creacion__lt=fin)
        return Response(PedidoSerializer(pedidos, many=True).data)

    def post(self, request):
        entrada = CrearPedidoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        try:
            pedido = servicios.crear_pedido(
                request.user,
                [(i['plato'], i['cantidad']) for i in datos['items']],
                mesa=datos.get('mesa'),
                observaciones=datos.get('observaciones', ''),
                domicilio=datos.get('domicilio'),
            )
        except servicios.ErrorPedido as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)


class CocinaAPI(generics.ListAPIView):
    """GET /api/cocina/ → pedidos pendientes, en preparación y listos (más antiguos primero)."""
    permission_classes = [RolPermitido]
    roles = ['ADMINISTRADOR', 'COCINA']
    serializer_class = PedidoSerializer

    def get_queryset(self):
        return _pedidos().filter(
            estado__in=[Pedido.Estado.PENDIENTE, Pedido.Estado.EN_PREPARACION, Pedido.Estado.LISTO]
        ).order_by('fecha_creacion')


class CambiarEstadoAPI(APIView):
    """PATCH /api/pedidos/<id>/estado/  con {"estado": "LISTO"}."""
    permission_classes = [RolPermitido]
    roles = ['ADMINISTRADOR', 'COCINA', 'MESERO']

    def patch(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        entrada = EstadoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        nuevo = entrada.validated_data['estado']
        permitidos = ESTADOS_POR_ROL.get(request.user.rol, set())
        if not request.user.is_superuser and nuevo not in permitidos:
            return Response({'error': 'Tu rol no puede poner ese estado.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            pedido = servicios.cambiar_estado(pedido, nuevo)
        except servicios.ErrorPedido as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PedidoSerializer(_pedidos().get(pk=pedido.pk)).data)


class InsumoAlertasAPI(generics.ListAPIView):
    """GET /api/insumos/alertas/ → insumos en o por debajo del mínimo."""
    permission_classes = [RolPermitido]
    roles = ['ADMINISTRADOR']
    serializer_class = InsumoAlertaSerializer

    def get_queryset(self):
        return Insumo.objects.filter(existencia__lte=F('cantidad_minima'))
