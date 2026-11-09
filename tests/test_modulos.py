"""Pruebas reales de MariaDB en una base temporal; nunca escriben en la base configurada.

Ejecutar con FARMACIA_PRUEBAS_DB=1 y `py -B -m unittest discover -s tests -v`.
La cuenta configurada necesita permiso CREATE/DROP DATABASE.
"""
import os
import re
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

import mysql.connector
import config
import servicios
from seguridad import cifrar_contrasena, verificar_contrasena


class SeguridadTests(unittest.TestCase):
    def test_hash_y_compatibilidad(self):
        clave = ' contraseña segura '
        cifrada = cifrar_contrasena(clave)
        self.assertNotEqual(clave, cifrada)
        self.assertTrue(verificar_contrasena(clave, cifrada))
        self.assertFalse(verificar_contrasena(clave.strip(), cifrada))
        self.assertTrue(verificar_contrasena('legacy', 'legacy'))
        self.assertFalse(verificar_contrasena('incorrecta', 'legacy'))
        self.assertFalse(verificar_contrasena('a' * 73, cifrada))


@unittest.skipUnless(os.environ.get('FARMACIA_PRUEBAS_DB') == '1', 'Requiere base temporal explícita')
class IntegracionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nombre = 'farmacia_test_' + uuid4().hex
        cls.opciones = dict(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD)
        cls.admin_db = mysql.connector.connect(**cls.opciones)
        cur = cls.admin_db.cursor()
        cur.execute(f'CREATE DATABASE `{cls.nombre}` CHARACTER SET utf8mb4')
        cur.close()
        cls.addClassCleanup(cls.limpiar_base)
        cls.parche = patch('servicios.conectar', cls.conectar_pruebas)
        cls.parche.start()
        cls.addClassCleanup(cls.parche.stop)
        # Probar tanto el esquema del archivo como el de la instalación existente.
        c = cls.conectar_pruebas(); cur = c.cursor()
        tablas = ['usuarios','empleados','ubicaciones','medicamentos','ventas','detalle_venta','movimientos_inventario']
        if os.environ.get('FARMACIA_ESQUEMA_ARCHIVO') == '1':
            esquema = Path(__file__).resolve().parents[1] / 'database' / 'farmacia_local.sql'
            sql = esquema.read_text(encoding='utf-8')
            for nombre in tablas:
                statement = re.search(r'CREATE TABLE ' + nombre + r' \(.*?ENGINE = InnoDB;', sql, re.S).group()
                cur.execute(statement)
        else:
            origen = mysql.connector.connect(**cls.opciones, database=config.DB_NAME)
            lector = origen.cursor()
            for nombre in tablas:
                lector.execute('SHOW CREATE TABLE ' + nombre)
                cur.execute(lector.fetchone()[1])
            lector.close(); origen.close()
        cur.close()
        from migrar import aplicar
        aplicar(c)
        c.close()

    @classmethod
    def conectar_pruebas(cls):
        return mysql.connector.connect(**cls.opciones, database=cls.nombre)

    @classmethod
    def limpiar_base(cls):
        assert re.fullmatch(r'farmacia_test_[0-9a-f]{32}', cls.nombre)
        assert cls.nombre != config.DB_NAME
        cur = cls.admin_db.cursor()
        cur.execute(f'DROP DATABASE `{cls.nombre}`')
        cur.close(); cls.admin_db.close()

    def sql(self, sentencia, params=(), filas=False):
        c = self.conectar_pruebas(); cur = c.cursor(dictionary=True)
        try:
            cur.execute(sentencia, params)
            resultado = cur.fetchall() if filas else cur.lastrowid
            c.commit()
            return resultado
        finally:
            cur.close(); c.close()

    def setUp(self):
        for tabla in ['encuesta_autor','encuestas',
                      'movimientos_inventario','detalle_venta','ventas','empleados','medicamentos','ubicaciones','usuarios']:
            self.sql('DELETE FROM ' + tabla)
        aid = self.sql("INSERT INTO usuarios (nombre,usuario,contrasena,rol) VALUES ('Admin','admin','legacy','ADMIN')")
        uid = self.sql("INSERT INTO usuarios (nombre,usuario,contrasena,rol) VALUES ('Empleado','empleado','legacy','EMPLEADO')")
        self.admin = dict(idUsuario=aid, nombre='Admin', rol='ADMIN')
        self.empleado = dict(idUsuario=uid, nombre='Empleado', rol='EMPLEADO')
        self.producto = self.sql("INSERT INTO medicamentos (nombre,cantidad,precioVenta,stockMinimo) VALUES ('Producto prueba',10,10.15,3)")
        self.datos = dict(nombre='Empleado de prueba', fechaNacimiento=date(1995,1,2),
            rfc='TEST950102AB1', direccion='Calle de prueba 10', telefono='5551234567', identificacion='Folio de prueba')
        self.cuenta = dict(usuario='nuevo', rol='EMPLEADO', contrasena='clave-segura')

    def linea(self, cantidad=2):
        return dict(idMedicamento=self.producto, cantidad=cantidad, precioUnitario=Decimal('10.15'))

    def test_venta_detalle_inventario_y_filtros(self):
        vid, total, alertas = servicios.registrar_venta(self.empleado, [self.linea(7)], 'TARJETA')
        self.assertEqual(total, Decimal('71.05'))
        self.assertEqual(len(alertas), 1)
        venta, detalle = servicios.consultar_venta(self.admin, vid)
        self.assertEqual(venta['metodoPago'], 'TARJETA')
        self.assertEqual(detalle[0]['cantidad'], 7)
        self.assertEqual(self.sql('SELECT cantidad FROM medicamentos', filas=True)[0]['cantidad'], 3)
        mov = self.sql('SELECT * FROM movimientos_inventario', filas=True)[0]
        self.assertEqual((mov['idVenta'],mov['cantidadAnterior'],mov['cantidadNueva']), (vid,10,3))
        self.assertEqual(len(servicios.listar_ventas(self.empleado, str(vid))), 1)
        self.assertEqual(servicios.listar_ventas(self.admin, desde=date(2000,1,1), hasta=date(2000,1,2)), [])

    def test_ventas_invalidas_no_escriben(self):
        for lineas, metodo in [([], 'EFECTIVO'),([self.linea(11)], 'EFECTIVO'),
                ([self.linea(0)],'EFECTIVO'),([self.linea()],'INVALIDO'),
                ([self.linea(),self.linea()],'EFECTIVO'),
                ([{**self.linea(),'precioUnitario':Decimal('9.00')}],'EFECTIVO')]:
            with self.assertRaises(ValueError):
                servicios.registrar_venta(self.empleado, lineas, metodo)
        self.assertEqual(self.sql('SELECT * FROM ventas', filas=True), [])
        self.assertEqual(self.sql('SELECT cantidad FROM medicamentos', filas=True)[0]['cantidad'], 10)
        self.sql('UPDATE medicamentos SET activo=0')
        with self.assertRaises(ValueError):
            servicios.registrar_venta(self.empleado,[self.linea()],'EFECTIVO')

    def test_rollback_si_falla_movimiento(self):
        self.sql("""CREATE TRIGGER fallo_prueba BEFORE INSERT ON movimientos_inventario
                    FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Fallo simulado'""")
        try:
            with self.assertRaises(ValueError):
                servicios.registrar_venta(self.empleado,[self.linea()],'EFECTIVO')
            self.assertEqual(self.sql('SELECT * FROM ventas', filas=True), [])
            self.assertEqual(self.sql('SELECT * FROM detalle_venta', filas=True), [])
            self.assertEqual(self.sql('SELECT cantidad FROM medicamentos', filas=True)[0]['cantidad'], 10)
        finally:
            self.sql('DROP TRIGGER fallo_prueba')

    def test_ventas_simultaneas_no_sobrevenden(self):
        def vender(usuario):
            try:
                servicios.registrar_venta(usuario, [self.linea(7)], 'EFECTIVO')
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(vender, [self.admin,self.empleado]))
        self.assertEqual(sorted(resultados), [False, True])
        self.assertEqual(self.sql('SELECT cantidad FROM medicamentos', filas=True)[0]['cantidad'], 3)

    def test_crud_empleados_y_cuentas(self):
        eid = servicios.guardar_empleado(self.admin, self.datos, self.cuenta)
        registro = servicios.consultar_empleado(self.admin, eid)
        clave = self.sql('SELECT contrasena FROM usuarios WHERE idUsuario=%s', (registro['idUsuario'],), True)[0]['contrasena']
        self.assertTrue(verificar_contrasena(self.cuenta['contrasena'], clave))
        servicios.guardar_empleado(self.admin, {**self.datos,'nombre':'Nombre modificado'},
                                  {**self.cuenta,'contrasena':''}, eid)
        self.assertEqual(servicios.listar_empleados(self.admin,'modificado')[0]['idEmpleado'], eid)
        servicios.cambiar_empleado(self.admin, eid, 'desactivar')
        self.assertEqual(servicios.consultar_empleado(self.admin,eid)['activo'], 0)
        cuenta = {'idUsuario':registro['idUsuario']}
        with self.assertRaises(ValueError): servicios.listar_ventas(cuenta)
        servicios.cambiar_empleado(self.admin, eid, 'reactivar')
        vid, _, _ = servicios.registrar_venta(cuenta,[self.linea()],'TRANSFERENCIA')
        servicios.cambiar_empleado(self.admin,eid,'eliminar')
        with self.assertRaises(ValueError): servicios.consultar_empleado(self.admin,eid)
        self.assertEqual(servicios.consultar_venta(self.admin,vid)[0]['idUsuario'],registro['idUsuario'])
        with self.assertRaises(ValueError): servicios.listar_ventas(cuenta)

    def test_permisos_y_cuenta_propia(self):
        with self.assertRaises(ValueError): servicios.listar_empleados(self.empleado)
        with self.assertRaises(ValueError): servicios.guardar_empleado(self.empleado,self.datos)
        vid, _, _ = servicios.registrar_venta(self.admin,[self.linea()],'EFECTIVO')
        self.assertEqual(servicios.listar_ventas(self.empleado), [])
        with self.assertRaises(ValueError): servicios.consultar_venta(self.empleado,vid)
        eid = self.sql('INSERT INTO empleados (nombre,idUsuario) VALUES (%s,%s)', ('Admin',self.admin['idUsuario']))
        for accion in ['eliminar','desactivar']:
            with self.assertRaises(ValueError): servicios.cambiar_empleado(self.admin,eid,accion)
        with self.assertRaises(ValueError):
            servicios.guardar_empleado(self.admin,self.datos,{**self.cuenta,'usuario':'admin'},eid)
        self.sql('UPDATE usuarios SET activo=0 WHERE idUsuario=%s',(self.empleado['idUsuario'],))
        with self.assertRaises(ValueError): servicios.registrar_venta(self.empleado,[self.linea()],'EFECTIVO')

    def test_duplicados_y_validaciones(self):
        servicios.guardar_empleado(self.admin,self.datos,self.cuenta)
        for datos, cuenta in [(self.datos,None), ({**self.datos,'rfc':'OTRO950102AB1'},self.cuenta),
                              ({**self.datos,'nombre':''},None),({**self.datos,'fechaNacimiento':date(2999,1,1)},None)]:
            with self.assertRaises(ValueError): servicios.guardar_empleado(self.admin,datos,cuenta)
        self.assertEqual(len(servicios.listar_empleados(self.admin)),1)

    def test_interfaz_y_login(self):
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QWidget
        from empleados import Empleados, DialogoEmpleado
        from ventas import Ventas, DialogoVenta, DialogoDetalleVenta
        from login import Login
        app = QApplication.instance() or QApplication([])
        # El plugin offscreen de Qt en Windows no carga las fuentes del sistema.
        from PyQt6.QtGui import QFontDatabase, QFont
        for fuente in ['arial.ttf','arialbd.ttf']:
            ruta = Path('C:/Windows/Fonts') / fuente
            if ruta.exists(): QFontDatabase.addApplicationFont(str(ruta))
        app.setFont(QFont('Arial',10))
        with patch.object(QMessageBox,'warning') as aviso, patch.object(QMessageBox,'information'), \
             patch.object(QMessageBox,'critical') as error, patch('ventas.confirmar',return_value=True):
            empleados = Empleados(self.admin); empleados.recargar()
            form = DialogoEmpleado(self.admin)
            for clave,campo in form.campos.items(): campo.setText(self.datos[clave])
            from PyQt6.QtCore import QDate
            form.fecha.setDate(QDate(1995,1,2))
            form.con_cuenta.setChecked(True)
            form.nombre_usuario.setText('nuevo')
            form.clave.setText('clave-segura'); form.repetir.setText('clave-segura')
            form.guardar()
            self.assertEqual(form.result(), QDialog.DialogCode.Accepted)
            empleados.recargar(); self.assertEqual(empleados.tabla.rowCount(),1)
            dialogo = DialogoVenta(self.empleado)
            dialogo.resultados.selectRow(0); dialogo.agregar()
            dialogo.guardar()
            self.assertEqual(dialogo.result(), QDialog.DialogCode.Accepted)
            ventas = Ventas(self.admin); ventas.recargar()
            self.assertEqual(ventas.tabla.rowCount(),1)
            detalle = DialogoDetalleVenta(*servicios.consultar_venta(self.admin, dialogo.id_venta))
            with patch('login.conectar',self.conectar_pruebas), patch('principal.Principal',return_value=QWidget()):
                login = Login(); login.txt_usuario.setText('nuevo'); login.txt_contrasena.setText('clave-segura')
                login.iniciar_sesion()
                self.assertIsNotNone(login.ventana_principal)
                self.assertTrue(login.ventana_principal.isFullScreen())
                login.ventana_principal.close()
            from principal import Principal
            with patch('mapa.conectar',self.conectar_pruebas), \
                 patch('inventario.conectar',self.conectar_pruebas), \
                 patch('medicamentos.conectar',self.conectar_pruebas):
                principal = Principal(self.admin)
                principal.abrir_ventas()
                self.assertIs(principal.paginas.currentWidget(), principal.pagina_ventas)
                principal.abrir_empleados()
                self.assertIs(principal.paginas.currentWidget(), principal.pagina_empleados)
                principal_empleado = Principal(self.empleado)
                self.assertTrue(principal_empleado.btn_empleados.isHidden())
                principal_empleado.abrir_ventas()
                self.assertEqual(principal_empleado.pagina_ventas.tabla.rowCount(),1)
                principal.pagina_buscar.detener_parpadeo()
                principal_empleado.pagina_buscar.detener_parpadeo()
                principal.close(); principal_empleado.close()
            aviso.assert_not_called(); error.assert_not_called()
            # Renderizar widgets reales con datos ficticios para revisar el diseño.
            destino = os.environ.get('FARMACIA_CAPTURAS')
            if destino:
                for nombre,widget in [('empleados',empleados),('ventas',ventas),('empleado_formulario',form),
                                       ('venta_formulario',dialogo),('venta_detalle',detalle)]:
                    if not isinstance(widget,QDialog): widget.resize(1000,650)
                    widget.show(); app.processEvents()
                    widget.grab().save(str(Path(destino) / (nombre + '.png')))
                    widget.hide()
                principal.show(); principal.abrir_empleados(); app.processEvents()
                principal.grab().save(str(Path(destino) / 'principal_empleados.png'))
                principal.hide()
            for widget in [form,empleados,dialogo,ventas,detalle]: widget.deleteLater()
            app.processEvents()

    def test_crud_empleados_desde_botones(self):
        """Usar señales Qt reales: una llamada directa a guardar no detecta clicked(bool)."""
        import sys
        from PyQt6.QtCore import QDate, QTimer
        from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton
        from empleados import Empleados, DialogoEmpleado
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        app = QApplication.instance() or QApplication([])
        fallos = []

        def capturar(tipo, valor, traceback):
            fallos.append(f'{tipo.__name__}: {valor}')

        def abrir_y_operar(boton, operacion):
            def operar():
                modal = app.activeModalWidget()
                try:
                    self.assertIsInstance(modal, DialogoEmpleado)
                    operacion(modal)
                except Exception as exc:
                    fallos.append(str(exc))
                finally:
                    # No dejar exec() bloqueado si una señal causa una excepción.
                    if modal is not None and modal.isVisible():
                        modal.reject()
            QTimer.singleShot(0, operar)
            boton.click()
            self.assertEqual(fallos, [])

        with patch.object(sys, 'excepthook', capturar), \
             patch.object(QMessageBox, 'warning') as aviso, \
             patch('empleados.confirmar', return_value=True):
            pagina = Empleados(self.admin)
            pagina.recargar()
            registrar = next(b for b in pagina.findChildren(QPushButton) if b.text() == 'Registrar empleado')

            def alta(form):
                for clave, campo in form.campos.items():
                    campo.setText(self.datos[clave])
                form.fecha.setDate(QDate(1995,1,2))
                form.con_cuenta.setChecked(True)
                form.nombre_usuario.setText('nuevo')
                form.clave.setText('clave-segura')
                form.repetir.setText('clave-segura')
                form.btn_guardar.click()

            abrir_y_operar(registrar, alta)
            self.assertEqual(pagina.tabla.rowCount(), 1)
            pagina.tabla.selectRow(0)

            def consultar(form):
                self.assertTrue(form.campos['nombre'].isReadOnly())
                self.assertEqual(form.campos['nombre'].text(), self.datos['nombre'])
                cerrar = next(b for b in form.findChildren(QPushButton) if b.text() == 'Cerrar')
                cerrar.click()

            abrir_y_operar(pagina.btn_consultar, consultar)

            def editar(form):
                form.campos['nombre'].setText('Cambio desde botón')
                form.btn_guardar.click()

            abrir_y_operar(pagina.btn_editar, editar)
            self.assertEqual(pagina.tabla.item(0,1).text(), 'Cambio desde botón')
            pagina.tabla.selectRow(0)
            pagina.btn_estado.click()
            self.assertEqual(pagina.tabla.rowCount(), 0)
            pagina.estado.setCurrentIndex(1)
            self.assertEqual(pagina.tabla.rowCount(), 1)
            pagina.tabla.selectRow(0)
            self.assertEqual(pagina.btn_estado.text(), 'Reactivar')
            pagina.btn_estado.click()
            self.assertEqual(pagina.tabla.rowCount(), 0)
            pagina.estado.setCurrentIndex(0)
            pagina.tabla.selectRow(0)
            pagina.btn_eliminar.click()
            self.assertEqual(pagina.tabla.rowCount(), 0)
            self.assertEqual(servicios.listar_empleados(self.admin), [])
            cuenta = self.sql("SELECT activo FROM usuarios WHERE usuario='nuevo'", filas=True)[0]
            self.assertEqual(cuenta['activo'], 0)
            self.assertEqual(fallos, [])
            aviso.assert_not_called()
            pagina.deleteLater()
            app.processEvents()


if __name__ == '__main__':
    unittest.main()
