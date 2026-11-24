"""Los serializadores convierten los modelos a JSON (y validan el JSON que llega)."""
from django.utils import timezone
from rest_framework import serializers

from apps.carta.models import Plato
from apps.inventario.models import Insumo
from apps.pedidos.models import DetallePedido, Domicilio, Mesa, Pedido


class PlatoSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(source='categoria.nombre')

    class Meta:
        model = Plato
        fields = ['id', 'nombre', 'categoria', 'precio']


class DetallePedidoSerializer(serializers.ModelSerializer):
    plato = serializers.CharField(source='plato.nombre')

    class Meta:
        model = DetallePedido
        fields = ['plato', 'cantidad', 'precio_unitario', 'subtotal']


class DomicilioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domicilio
        fields = ['nombre_cliente', 'direccion', 'telefono']


class PedidoSerializer(serializers.ModelSerializer):
    """Pedido completo para mostrar (por ejemplo, en la pantalla de cocina)."""
    estado_texto = serializers.CharField(source='get_estado_display')
    destino = serializers.CharField()
    mesero = serializers.CharField(source='mesero.get_full_name')
    detalles = DetallePedidoSerializer(many=True)
    domicilio = DomicilioSerializer(read_only=True)
    total = serializers.DecimalField(source='calcular_total', max_digits=12, decimal_places=2)
    minutos = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ['id', 'tipo', 'estado', 'estado_texto', 'destino', 'mesero', 'observaciones',
                  'fecha_creacion', 'minutos', 'detalles', 'domicilio', 'total']

    def get_minutos(self, pedido):
        """Minutos desde que se creó el pedido."""
        return int((timezone.now() - pedido.fecha_creacion).total_seconds() // 60)


class ItemSerializer(serializers.Serializer):
    plato = serializers.PrimaryKeyRelatedField(queryset=Plato.objects.filter(activo=True))
    cantidad = serializers.IntegerField(min_value=1)


class CrearPedidoSerializer(serializers.Serializer):
    """Datos que llegan para crear un pedido por la API."""
    mesa = serializers.PrimaryKeyRelatedField(queryset=Mesa.objects.all(), required=False, allow_null=True)
    observaciones = serializers.CharField(required=False, allow_blank=True, default='')
    items = ItemSerializer(many=True)
    domicilio = DomicilioSerializer(required=False, allow_null=True)


class EstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Pedido.Estado.choices)


class InsumoAlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = ['id', 'nombre', 'unidad', 'existencia', 'cantidad_minima']
