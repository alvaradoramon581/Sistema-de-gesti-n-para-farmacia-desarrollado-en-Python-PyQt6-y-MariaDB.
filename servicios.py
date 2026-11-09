"""Operaciones de ventas y empleados sobre el esquema existente, sin DDL automático."""
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
import re

from mysql.connector import Error, IntegrityError
from conexion import conectar
from seguridad import cifrar_contrasena


@contextmanager
def transaccion():
    conexion = conectar()
    if conexion is None:
        raise ValueError('No se pudo conectar con la base de datos local.')
    cursor = None
    try:
        conexion.start_transaction()
        cursor = conexion.cursor(dictionary=True)
        yield cursor
        conexion.commit()
    except IntegrityError as exc:
        conexion.rollback()
        raise ValueError('El usuario o RFC ya existe, o el registro tiene datos relacionados.') from exc
    except Error as exc:
        conexion.rollback()
        raise ValueError('No se pudo completar la operación. Actualice e intente nuevamente.') from exc
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def autorizar(cursor, usuario, administrador=False, bloquear=False):
    # Consultar el rol vigente: una sesión abierta no conserva permisos revocados.
    cursor.execute('SELECT idUsuario, rol, activo FROM usuarios WHERE idUsuario=%s'
                   + (' FOR UPDATE' if bloquear else ''), (usuario['idUsuario'],))
    actual = cursor.fetchone()
    if not actual or not actual['activo'] or actual['rol'] not in ('ADMIN', 'EMPLEADO'):
        raise ValueError('La cuenta está inactiva. Inicie sesión nuevamente.')
    if administrador and actual['rol'] != 'ADMIN':
        raise ValueError('Solo el administrador puede gestionar empleados.')
    return actual


def buscar_productos(usuario, texto=''):
    with transaccion() as cur:
        autorizar(cur, usuario)
        patron = '%' + texto.strip() + '%'
        cur.execute('''SELECT m.idMedicamento, m.nombre, m.presentacion, m.codigoBarras,
            m.cantidad, m.precioVenta, m.stockMinimo,
            CONCAT_WS(' / ', u.codigo, CONCAT('Nivel ',u.nivel)) AS ubicacion
            FROM medicamentos m LEFT JOIN ubicaciones u ON u.idUbicacion=m.idUbicacion
            WHERE m.activo=1 AND (m.nombre LIKE %s OR m.codigoBarras LIKE %s
              OR m.principioActivo LIKE %s OR m.fabricante LIKE %s)
            ORDER BY m.nombre LIMIT 200''', (patron,) * 4)
        return cur.fetchall()


def registrar_venta(usuario, lineas, metodo):
    if metodo not in ('EFECTIVO', 'TARJETA', 'TRANSFERENCIA'):
        raise ValueError('Seleccione un método de pago válido.')
    if not lineas:
        raise ValueError('Agregue al menos un producto a la venta.')
    ids = set()
    for linea in lineas:
        if type(linea['cantidad']) is not int or not 1 <= linea['cantidad'] <= 2147483647:
            raise ValueError('La cantidad debe ser un entero mayor que cero.')
        if linea['idMedicamento'] in ids:
            raise ValueError('Hay productos repetidos en la venta.')
        ids.add(linea['idMedicamento'])
    with transaccion() as cur:
        autorizar(cur, usuario, bloquear=True)
        total = Decimal('0.00')
        productos = []
        # Orden fijo y bloqueo de filas para evitar sobreventa entre dos cajas.
        for linea in sorted(lineas, key=lambda item: item['idMedicamento']):
            cur.execute('''SELECT idMedicamento, nombre, activo, cantidad, precioVenta,
                           stockMinimo, (fechaCaducidad <= CURDATE()) AS caducado
                           FROM medicamentos WHERE idMedicamento=%s FOR UPDATE''',
                        (linea['idMedicamento'],))
            producto = cur.fetchone()
            if not producto or not producto['activo']:
                raise ValueError('Uno de los productos ya no está activo. Retírelo de la venta.')
            if producto['caducado']:
                raise ValueError(f"{producto['nombre']} ha caducado o vence hoy. Revise su ficha en Medicamentos.")
            if producto['cantidad'] < linea['cantidad']:
                raise ValueError(f"Existencia insuficiente de {producto['nombre']}: {producto['cantidad']}.")
            if producto['precioVenta'] != Decimal(str(linea['precioUnitario'])):
                raise ValueError(f"Cambió el precio de {producto['nombre']}. Retírelo y agréguelo nuevamente.")
            importe = producto['precioVenta'] * linea['cantidad']
            total += importe
            productos.append((producto, linea['cantidad'], importe))
        if total > Decimal('99999999.99'):
            raise ValueError('El total excede el límite de una venta.')
        cur.execute('''INSERT INTO ventas (idUsuario, metodoPago, subtotal, total)
                       VALUES (%s,%s,%s,%s)''', (usuario['idUsuario'], metodo, total, total))
        id_venta = cur.lastrowid
        alertas = []
        for producto, cantidad, importe in productos:
            nueva = producto['cantidad'] - cantidad
            cur.execute('''INSERT INTO detalle_venta
                (idVenta,idMedicamento,cantidad,precioUnitario,subtotal) VALUES (%s,%s,%s,%s,%s)''',
                (id_venta, producto['idMedicamento'], cantidad, producto['precioVenta'], importe))
            cur.execute('UPDATE medicamentos SET cantidad=%s WHERE idMedicamento=%s',
                        (nueva, producto['idMedicamento']))
            cur.execute('''INSERT INTO movimientos_inventario
                (idMedicamento,idUsuario,idVenta,tipo,cantidad,cantidadAnterior,cantidadNueva,descripcion)
                VALUES (%s,%s,%s,'VENTA',%s,%s,%s,%s)''',
                (producto['idMedicamento'], usuario['idUsuario'], id_venta, cantidad,
                 producto['cantidad'], nueva, f'Venta #{id_venta}'))
            if nueva <= producto['stockMinimo']:
                alertas.append(f"{producto['nombre']}: {nueva} unidades (mínimo {producto['stockMinimo']})")
        return id_venta, total, alertas


def listar_ventas(usuario, texto='', desde=None, hasta=None):
    with transaccion() as cur:
        actual = autorizar(cur, usuario)
        sql = '''SELECT v.*, u.nombre AS vendedor FROM ventas v
                 JOIN usuarios u ON u.idUsuario=v.idUsuario WHERE 1=1'''
        params = []
        if actual['rol'] != 'ADMIN':
            sql += ' AND v.idUsuario=%s'
            params.append(usuario['idUsuario'])
        if texto.strip():
            sql += ' AND (CAST(v.idVenta AS CHAR) LIKE %s OR u.nombre LIKE %s)'
            params.extend(['%' + texto.strip() + '%'] * 2)
        if desde:
            sql += ' AND v.fecha >= %s'
            params.append(desde)
        if hasta:
            sql += ' AND v.fecha < DATE_ADD(%s, INTERVAL 1 DAY)'
            params.append(hasta)
        cur.execute(sql + ' ORDER BY v.fecha DESC, v.idVenta DESC', params)
        return cur.fetchall()


def consultar_venta(usuario, id_venta):
    with transaccion() as cur:
        actual = autorizar(cur, usuario)
        cur.execute('''SELECT v.*, u.nombre AS vendedor FROM ventas v
            JOIN usuarios u ON u.idUsuario=v.idUsuario WHERE v.idVenta=%s''', (id_venta,))
        venta = cur.fetchone()
        if not venta or (actual['rol'] != 'ADMIN' and venta['idUsuario'] != usuario['idUsuario']):
            raise ValueError('La venta no está disponible para este usuario.')
        cur.execute('''SELECT d.*, m.nombre, m.presentacion FROM detalle_venta d
            JOIN medicamentos m ON m.idMedicamento=d.idMedicamento
            WHERE d.idVenta=%s ORDER BY d.idDetalle''', (id_venta,))
        return venta, cur.fetchall()


EMPLEADO_SELECT = '''SELECT e.*, u.usuario, u.rol FROM empleados e
                    LEFT JOIN usuarios u ON u.idUsuario=e.idUsuario'''


def listar_empleados(usuario, texto='', estado=None):
    with transaccion() as cur:
        autorizar(cur, usuario, administrador=True)
        sql = EMPLEADO_SELECT + ''' WHERE (e.nombre LIKE %s OR e.rfc LIKE %s
            OR e.telefono LIKE %s OR e.direccion LIKE %s OR u.usuario LIKE %s)'''
        params = ['%' + texto.strip() + '%'] * 5
        if estado is not None:
            sql += ' AND e.activo=%s'
            params.append(estado)
        cur.execute(sql + ' ORDER BY e.nombre, e.idEmpleado', params)
        return cur.fetchall()


def consultar_empleado(usuario, id_empleado):
    with transaccion() as cur:
        autorizar(cur, usuario, administrador=True)
        cur.execute(EMPLEADO_SELECT + ' WHERE e.idEmpleado=%s', (id_empleado,))
        empleado = cur.fetchone()
        if not empleado:
            raise ValueError('El empleado ya no existe. Actualice la lista.')
        return empleado


def validar_empleado(datos):
    resultado = {}
    for clave, limite in [('nombre',100), ('rfc',13), ('direccion',200),
                          ('telefono',20), ('identificacion',100)]:
        valor = datos.get(clave, '').strip()
        if not valor or len(valor) > limite:
            raise ValueError(f'Complete {clave} (máximo {limite} caracteres).')
        resultado[clave] = valor
    nacimiento = datos.get('fechaNacimiento')
    if not isinstance(nacimiento, date) or not date(1900,1,1) <= nacimiento < date.today():
        raise ValueError('Ingrese una fecha de nacimiento válida, anterior a hoy.')
    resultado['fechaNacimiento'] = nacimiento
    resultado['rfc'] = resultado['rfc'].upper()
    if not re.fullmatch(r'[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}', resultado['rfc']):
        raise ValueError('El RFC debe contener 4 letras, 6 dígitos y 3 caracteres de homoclave.')
    if not re.fullmatch(r'[+\d ()-]{7,20}', resultado['telefono']) or len(re.sub(r'\D', '', resultado['telefono'])) < 7:
        raise ValueError('Ingrese un teléfono válido de al menos 7 dígitos.')
    return resultado


def bloquear_administracion(cur, usuario):
    # Serializa los cambios de cuentas y protege al último administrador activo.
    cur.execute('SELECT idUsuario FROM usuarios ORDER BY idUsuario FOR UPDATE')
    cur.fetchall()
    autorizar(cur, usuario, administrador=True)


def proteger_cuenta(cur, usuario, id_usuario, rol, activo):
    if id_usuario == usuario['idUsuario'] and (not activo or rol != 'ADMIN'):
        raise ValueError('No puede eliminar, desactivar ni quitar el rol de administrador a su propia cuenta.')
    cur.execute('SELECT rol, activo FROM usuarios WHERE idUsuario=%s', (id_usuario,))
    anterior = cur.fetchone()
    if anterior and anterior['activo'] and anterior['rol'] == 'ADMIN' and (not activo or rol != 'ADMIN'):
        cur.execute("SELECT COUNT(*) AS n FROM usuarios WHERE activo=1 AND rol='ADMIN'")
        if cur.fetchone()['n'] <= 1:
            raise ValueError('Debe conservar al menos un administrador activo.')


def guardar_empleado(usuario, datos, cuenta=None, id_empleado=None):
    datos = validar_empleado(datos)
    clave_hash = None
    if cuenta is not None:
        if not re.fullmatch(r'[\w.@-]{3,50}', cuenta.get('usuario', '')):
            raise ValueError('El usuario debe tener de 3 a 50 letras, números o caracteres . @ - _.')
        if cuenta.get('rol') not in ('ADMIN', 'EMPLEADO'):
            raise ValueError('Seleccione un rol válido.')
        if cuenta.get('contrasena'):
            clave_hash = cifrar_contrasena(cuenta['contrasena'])
    with transaccion() as cur:
        bloquear_administracion(cur, usuario)
        anterior = None
        if id_empleado is not None:
            cur.execute('SELECT * FROM empleados WHERE idEmpleado=%s FOR UPDATE', (id_empleado,))
            anterior = cur.fetchone()
            if not anterior:
                raise ValueError('El empleado ya no existe. Actualice la lista.')
        cur.execute('SELECT idEmpleado FROM empleados WHERE rfc=%s AND idEmpleado<>%s',
                    (datos['rfc'], id_empleado or 0))
        if cur.fetchone():
            raise ValueError('Ya existe un empleado con ese RFC.')
        id_usuario = anterior['idUsuario'] if anterior else None
        activo = anterior['activo'] if anterior else 1
        if id_usuario and cuenta is None:
            raise ValueError('Conserve los datos de la cuenta vinculada al empleado.')
        if cuenta is not None:
            if id_usuario:
                proteger_cuenta(cur, usuario, id_usuario, cuenta['rol'], activo)
                cur.execute('''UPDATE usuarios SET nombre=%s, usuario=%s, rol=%s
                               WHERE idUsuario=%s''',
                            (datos['nombre'], cuenta['usuario'], cuenta['rol'], id_usuario))
                if clave_hash:
                    cur.execute('UPDATE usuarios SET contrasena=%s WHERE idUsuario=%s', (clave_hash, id_usuario))
            else:
                if not clave_hash:
                    raise ValueError('Ingrese una contraseña para la nueva cuenta.')
                cur.execute('''INSERT INTO usuarios (nombre,usuario,contrasena,rol,activo)
                               VALUES (%s,%s,%s,%s,%s)''',
                            (datos['nombre'], cuenta['usuario'], clave_hash, cuenta['rol'], activo))
                id_usuario = cur.lastrowid
        valores = (datos['nombre'], datos['fechaNacimiento'], datos['rfc'], datos['direccion'],
                   datos['telefono'], datos['identificacion'], id_usuario)
        if anterior:
            cur.execute('''UPDATE empleados SET nombre=%s, fechaNacimiento=%s, rfc=%s,
                direccion=%s, telefono=%s, identificacion=%s, idUsuario=%s WHERE idEmpleado=%s''',
                valores + (id_empleado,))
        else:
            cur.execute('''INSERT INTO empleados
                (nombre,fechaNacimiento,rfc,direccion,telefono,identificacion,idUsuario)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''', valores)
            id_empleado = cur.lastrowid
        return id_empleado


def cambiar_empleado(usuario, id_empleado, accion):
    if accion not in ('eliminar', 'desactivar', 'reactivar'):
        raise ValueError('Acción inválida.')
    with transaccion() as cur:
        bloquear_administracion(cur, usuario)
        cur.execute('SELECT * FROM empleados WHERE idEmpleado=%s FOR UPDATE', (id_empleado,))
        empleado = cur.fetchone()
        if not empleado:
            raise ValueError('El empleado ya no existe. Actualice la lista.')
        activo = int(accion == 'reactivar')
        if empleado['idUsuario']:
            cur.execute('SELECT rol FROM usuarios WHERE idUsuario=%s', (empleado['idUsuario'],))
            rol = cur.fetchone()['rol']
            proteger_cuenta(cur, usuario, empleado['idUsuario'], rol, activo)
            cur.execute('UPDATE usuarios SET activo=%s WHERE idUsuario=%s', (activo, empleado['idUsuario']))
        if accion == 'eliminar':
            # La cuenta queda inactiva: las ventas y sus autores no se borran.
            cur.execute('DELETE FROM empleados WHERE idEmpleado=%s', (id_empleado,))
        else:
            cur.execute('UPDATE empleados SET activo=%s WHERE idEmpleado=%s', (activo, id_empleado))


def movimiento_manual(usuario, medicamento, tipo, cantidad, descripcion, esperada):
    if tipo not in ('ENTRADA', 'DEVOLUCION', 'AJUSTE') or type(cantidad) is not int or cantidad < 0:
        raise ValueError('Movimiento inválido.')
    if cantidad == 0 and tipo != 'AJUSTE':
        raise ValueError('Indique una cantidad mayor que cero.')
    if len(descripcion) > 255 or (tipo != 'ENTRADA' and not descripcion.strip()):
        raise ValueError('Indique el motivo (máximo 255 caracteres).')
    with transaccion() as cur:
        autorizar(cur, usuario, bloquear=True)
        cur.execute('SELECT cantidad, activo FROM medicamentos WHERE idMedicamento=%s FOR UPDATE', (medicamento,))
        producto = cur.fetchone()
        if not producto or not producto['activo']:
            raise ValueError('El medicamento no existe o está inactivo.')
        anterior = producto['cantidad']
        if anterior != esperada:
            raise ValueError('La existencia cambió. Actualice y seleccione nuevamente el medicamento.')
        if tipo == 'ENTRADA':
            nueva = anterior + cantidad
        elif tipo == 'DEVOLUCION':
            nueva = anterior - cantidad
        else:
            nueva = cantidad
        if not 0 <= nueva <= 2147483647:
            raise ValueError('Existencia fuera de rango.')
        diferencia = abs(nueva - anterior)
        if diferencia == 0:
            raise ValueError('La existencia no cambia.')
        cur.execute('UPDATE medicamentos SET cantidad=%s WHERE idMedicamento=%s', (nueva, medicamento))
        cur.execute('''INSERT INTO movimientos_inventario
            (idMedicamento,idUsuario,tipo,cantidad,cantidadAnterior,cantidadNueva,descripcion)
            VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            (medicamento, usuario['idUsuario'], tipo, diferencia, anterior, nueva, descripcion.strip() or None))
        return nueva
