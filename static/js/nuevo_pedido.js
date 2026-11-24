// Pantalla "Nuevo pedido": botones + y −, resumen y total en vivo.
const formato = new Intl.NumberFormat('es-CO');

function actualizarResumen() {
  const lista = document.getElementById('resumen');
  let total = 0;
  lista.innerHTML = '';
  document.querySelectorAll('.cantidad').forEach(function (campo) {
    const cantidad = parseInt(campo.value) || 0;
    if (cantidad > 0) {
      const subtotal = cantidad * parseInt(campo.dataset.precio);
      total += subtotal;
      lista.innerHTML += '<li class="d-flex justify-content-between"><span>' + cantidad + ' × ' +
        campo.dataset.nombre + '</span><span>$' + formato.format(subtotal) + '</span></li>';
    }
  });
  if (total === 0) lista.innerHTML = '<li class="text-muted">Aún no hay platos.</li>';
  document.getElementById('total').textContent = '$' + formato.format(total);
}

// Botones + y −
document.querySelectorAll('[data-mas], [data-menos]').forEach(function (boton) {
  boton.addEventListener('click', function () {
    const id = boton.dataset.mas || boton.dataset.menos;
    const campo = document.getElementById('cantidad_' + id);
    const valor = (parseInt(campo.value) || 0) + (boton.dataset.mas ? 1 : -1);
    campo.value = Math.max(0, valor);
    actualizarResumen();
  });
});
document.querySelectorAll('.cantidad').forEach(function (c) { c.addEventListener('input', actualizarResumen); });

// Mostrar mesas o datos del domicilio según el tipo elegido
function mostrarTipo() {
  if (!document.getElementById('tipo-domicilio')) return;  // al editar no hay tipo
  const esDomicilio = document.getElementById('tipo-domicilio').checked;
  document.getElementById('seccion-mesa').classList.toggle('d-none', esDomicilio);
  document.getElementById('seccion-domicilio').classList.toggle('d-none', !esDomicilio);
}
document.querySelectorAll('input[name="tipo"]').forEach(function (r) { r.addEventListener('change', mostrarTipo); });
mostrarTipo();
actualizarResumen();
