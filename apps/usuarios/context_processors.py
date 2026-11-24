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
        ('Mesas', '#'),
        ('Reportes', '#'),
    ],
    'MESERO': [
        ('Inicio', '/'),
        ('Mesas', '#'),
        ('Nuevo pedido', '#'),
        ('Mis pedidos', '#'),
    ],
    'COCINA': [
        ('Inicio', '/'),
        ('Pedidos de cocina', '#'),
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
