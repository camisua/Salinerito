"""Menú lateral según el rol del usuario.

Un "context processor" agrega datos a TODAS las plantillas.
Así el menú se arma en un solo lugar y base.html lo muestra en cada página.
"""

MENU_POR_ROL = {
    'ADMINISTRADOR': [
        ('Panel', '/reportes/panel/'),
        ('Usuarios', '/admin/usuarios/usuario/'),
        ('Carta', '/carta/'),
        ('Insumos', '/inventario/'),
        ('Mesas', '/pedidos/mesas/'),
        ('Pedidos de hoy', '/pedidos/mis-pedidos/'),
        ('Cocina', '/pedidos/cocina/'),
        ('Caja', '/caja/'),
        ('Cierre de caja', '/caja/cierre/'),
        ('Reportes', '/reportes/'),
    ],
    'MESERO': [
        ('Inicio', '/'),
        ('Mesas', '/pedidos/mesas/'),
        ('Nuevo pedido', '/pedidos/nuevo/'),
        ('Mis pedidos', '/pedidos/mis-pedidos/'),
    ],
    'COCINA': [
        ('Inicio', '/'),
        ('Pedidos de cocina', '/pedidos/cocina/'),
    ],
    'CAJERO': [
        ('Inicio', '/'),
        ('Por cobrar', '/caja/'),
        ('Domicilios', '/caja/domicilios/'),
        ('Cierre de caja', '/caja/cierre/'),
    ],
}


def menu(request):
    if not request.user.is_authenticated:
        return {'menu': []}
    opciones = MENU_POR_ROL.get(request.user.rol, [])
    # La opción activa es la que más se parece a la dirección actual
    coincidencias = [e for _, e in opciones if e != '#' and request.path.startswith(e)]
    activa = max(coincidencias, key=len) if coincidencias else None
    return {'menu': [(nombre, enlace, enlace == activa) for nombre, enlace in opciones]}
