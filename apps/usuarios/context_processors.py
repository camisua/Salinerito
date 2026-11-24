"""Menú lateral según el rol del usuario.

Un "context processor" agrega datos a TODAS las plantillas.
Así el menú se arma en un solo lugar y base.html lo muestra en cada página.
"""

MENU_POR_ROL = {
    'ADMINISTRADOR': [
        ('Inicio', '/'),
        ('Usuarios', '/admin/usuarios/usuario/'),
        ('Carta', '/carta/'),
        ('Insumos', '/inventario/'),
        ('Mesas', '/pedidos/mesas/'),
        ('Pedidos de hoy', '/pedidos/mis-pedidos/'),
        ('Cocina', '/pedidos/cocina/'),
        ('Reportes', '#'),
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
        ('Por cobrar', '#'),
        ('Domicilios', '#'),
        ('Cierre de caja', '#'),
    ],
}


def menu(request):
    if request.user.is_authenticated:
        return {'menu': MENU_POR_ROL.get(request.user.rol, [])}
    return {'menu': []}
