// Tablero de cocina: pide los pedidos a la API y los muestra en tres columnas.
// GET  /api/cocina/                 → lista de pedidos activos (JSON)
// PATCH /api/pedidos/<id>/estado/   → cambia el estado

const SIGUIENTE = {
  PENDIENTE: ['EN_PREPARACION', 'Empezar'],
  EN_PREPARACION: ['LISTO', 'Marcar listo'],
  LISTO: ['ENTREGADO', 'Entregado'],
};

function tarjeta(pedido) {
  const platos = pedido.detalles.map(d => '<li>' + d.cantidad + ' × ' + d.plato + '</li>').join('');
  const obs = pedido.observaciones ? '<div class="small fst-italic mt-1">Obs: ' + pedido.observaciones + '</div>' : '';
  const [estado, texto] = SIGUIENTE[pedido.estado];
  return '<div class="tarjeta p-3 mb-2">' +
    '<div class="d-flex justify-content-between"><strong>#' + pedido.id + ' · ' + pedido.destino + '</strong>' +
    '<span class="small text-muted">hace ' + pedido.minutos + ' min</span></div>' +
    '<ul class="mb-1 mt-2 ps-3">' + platos + '</ul>' + obs +
    '<button class="btn btn-sm btn-salinero w-100 mt-2" onclick="cambiarEstado(' + pedido.id + ', \'' + estado + '\')">' + texto + '</button>' +
    '</div>';
}

async function cargar() {
  const respuesta = await fetch('/api/cocina/');
  if (!respuesta.ok) return;
  const pedidos = await respuesta.json();
  ['PENDIENTE', 'EN_PREPARACION', 'LISTO'].forEach(function (estado) {
    const grupo = pedidos.filter(p => p.estado === estado);
    document.getElementById('col-' + estado).innerHTML =
      grupo.map(tarjeta).join('') || '<p class="text-muted small">Sin pedidos.</p>';
    document.getElementById('n-' + estado).textContent = grupo.length;
  });
  document.getElementById('hora').textContent = new Date().toLocaleTimeString('es-CO');
}

async function cambiarEstado(id, estado) {
  const respuesta = await fetch('/api/pedidos/' + id + '/estado/', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
    body: JSON.stringify({ estado: estado }),
  });
  if (!respuesta.ok) {
    const error = await respuesta.json();
    alert(error.error || 'No se pudo cambiar el estado.');
  }
  cargar();
}

cargar();
setInterval(cargar, 10000);
