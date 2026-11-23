"""Auditorías independientes. Todas las escrituras ocurren en farmacia_test_* ."""
import os
import sys
import unittest
from unittest.mock import patch
import test_modulos as pruebas_base
from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton
from PyQt6.QtCore import QTimer,QDate


@unittest.skipUnless(os.environ.get('FARMACIA_PRUEBAS_DB')=='1','Requiere base temporal')
class Auditorias(unittest.TestCase):
    setUpClass = classmethod(pruebas_base.IntegracionTests.setUpClass.__func__)
    limpiar_base = classmethod(pruebas_base.IntegracionTests.limpiar_base.__func__)
    conectar_pruebas = classmethod(pruebas_base.IntegracionTests.conectar_pruebas.__func__)
    sql = pruebas_base.IntegracionTests.sql
    def setUp(self):
        pruebas_base.IntegracionTests.setUp(self)

    def interfaz(self):
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        self.app = QApplication.instance() or QApplication([])
        self.fallos = []
        p = patch.object(sys,'excepthook',lambda t,v,b:self.fallos.append(f'{t.__name__}: {v}'))
        p.start(); self.addCleanup(p.stop)
        p = patch.object(QMessageBox,'warning')
        self.aviso = p.start(); self.addCleanup(p.stop)
        from PyQt6.QtGui import QFontDatabase,QFont
        from pathlib import Path
        for nombre in ['arial.ttf','arialbd.ttf']:
            ruta=Path('C:/Windows/Fonts')/nombre
            if ruta.exists(): QFontDatabase.addApplicationFont(str(ruta))
        self.app.setFont(QFont('Arial',10))

    def pulsar(self,pagina,texto):
        next(b for b in pagina.findChildren(QPushButton) if b.text()==texto).click()
        self.assertEqual(self.fallos,[])

    def modal(self,pagina,texto,operacion):
        def actuar():
            ventana=self.app.activeModalWidget()
            try: operacion(ventana)
            except Exception as exc: self.fallos.append(str(exc))
            finally:
                if ventana and ventana.isVisible(): ventana.reject()
        QTimer.singleShot(0,actuar)
        self.pulsar(pagina,texto)

    def test_ficha_medicamento_por_botones(self):
        from medicamentos import Medicamentos
        from alertas import obtener_alertas
        self.interfaz()
        with patch('medicamentos.conectar', self.conectar_pruebas), patch.object(QMessageBox, 'information'), patch.object(QMessageBox, 'critical') as error:
            pagina = Medicamentos(self.admin)
            fecha = QDate.currentDate().addDays(12)

            def alta(form):
                pagina.txt_nombre.setText('Prueba de caducidad')
                pagina.txt_lote.setText('ABC-123')
                pagina.spn_cantidad.setValue(4)
                pagina.sin_caducidad.setChecked(False)
                pagina.fecha_caducidad.setDate(fecha)
                pagina.btn_confirmar.click()

            self.modal(pagina, 'Registrar medicamento', alta)
            registros = self.sql('SELECT * FROM medicamentos WHERE lote=%s', ('ABC-123',), True)
            self.assertEqual(len(registros), 1)
            self.assertEqual(registros[0]['fechaCaducidad'], fecha.toPyDate())
            self.assertTrue(any(r['lote']=='ABC-123' and r['tipo']=='Próxima caducidad' for r in obtener_alertas(self.admin)))
            fila = next(i for i in range(pagina.tabla.rowCount()) if pagina.tabla.item(i,0).text()=='Prueba de caducidad')
            pagina.tabla.selectRow(fila)

            def editar(form):
                self.assertEqual(pagina.txt_lote.text(), 'ABC-123')
                self.assertEqual(pagina.fecha_caducidad.date(), fecha)
                pagina.txt_lote.setText('DEF-456')
                pagina.sin_caducidad.setChecked(True)
                pagina.btn_confirmar.click()

            self.modal(pagina, 'Modificar', editar)
            modificado = self.sql('SELECT * FROM medicamentos WHERE idMedicamento=%s', (registros[0]['idMedicamento'],), True)[0]
            self.assertEqual(modificado['lote'], 'DEF-456')
            self.assertIsNone(modificado['fechaCaducidad'])
            self.assertEqual(modificado['cantidad'], 4)
            self.assertFalse(any(r['lote']=='ABC-123' for r in obtener_alertas(self.admin)))
            self.modal(pagina, 'Registrar medicamento', lambda form: form.reject())
            self.assertEqual(pagina.tabla.rowCount(),2)
            error.assert_not_called()
            self.aviso.assert_not_called()

    def test_existencias_sin_clasificacion(self):
        import servicios
        linea = {'idMedicamento': self.producto, 'cantidad': 1, 'precioUnitario': '10.15'}
        servicios.registrar_venta(self.admin, [linea], 'EFECTIVO')
        self.assertEqual(servicios.movimiento_manual(self.admin,self.producto,'AJUSTE',5,'Conteo',9), 5)
        self.sql('UPDATE medicamentos SET fechaCaducidad=CURDATE() WHERE idMedicamento=%s', (self.producto,))
        with self.assertRaisesRegex(ValueError, 'caducado'):
            servicios.registrar_venta(self.admin, [linea], 'EFECTIVO')
        self.assertEqual(self.sql('SELECT cantidad FROM medicamentos',filas=True)[0]['cantidad'],5)
        with self.assertRaisesRegex(ValueError,'existencia cambió'):
            servicios.movimiento_manual(self.admin,self.producto,'ENTRADA',2,'',9)

    def test_05_alertas_stock(self):
        from alertas import Alertas,obtener_alertas
        self.interfaz()
        self.sql('UPDATE medicamentos SET stockMinimo=10')
        r=obtener_alertas(self.empleado)
        self.assertEqual([x['urgente'] for x in r if x['tipo']=='Existencia baja'], [False])
        self.sql('UPDATE medicamentos SET cantidad=0')
        self.assertTrue(obtener_alertas(self.empleado)[0]['urgente'])
        self.sql('UPDATE medicamentos SET cantidad=10, stockMinimo=9')
        self.assertEqual(len([x for x in obtener_alertas(self.admin) if x['tipo']=='Existencia baja']),0)
        pagina=Alertas(self.admin); self.pulsar(pagina,'Actualizar')
        self.assertEqual(pagina.tabla.rowCount(),1)  # Sin fecha
        pagina.tipo.setCurrentText('Existencia baja')
        self.assertEqual(pagina.tabla.rowCount(),0)
        self.aviso.assert_not_called()

    def test_10_migracion_idempotente(self):
        from migrar import aplicar
        antes=self.sql('SELECT COUNT(*) AS n FROM medicamentos',filas=True)
        c=self.conectar_pruebas()
        try:
            aplicar(c); aplicar(c)
        finally: c.close()
        self.assertEqual(self.sql('SELECT COUNT(*) AS n FROM medicamentos',filas=True),antes)

    def test_06_alertas_caducidad(self):
        from datetime import date,timedelta
        from alertas import Alertas,obtener_alertas
        self.interfaz()
        for nombre, dias in [('AYER',-1), ('HOY',0), ('SIETE',7), ('OCHO',8), ('LIMITE',90), ('FUERA',91)]:
            self.sql('INSERT INTO medicamentos (nombre,lote,fechaCaducidad,cantidad) VALUES (%s,%s,%s,1)',
                     (nombre,nombre,date.today()+timedelta(days=dias)))
        alertas=obtener_alertas(self.admin,90)
        self.assertEqual(len([r for r in alertas if r['tipo']=='Caducado / vence hoy']),2)
        self.assertEqual([r['nombre'] for r in alertas if r['urgente']], ['AYER', 'HOY', 'SIETE'])
        pagina=Alertas(self.admin); pagina.tipo.setCurrentText('Próxima caducidad')
        self.assertEqual(pagina.tabla.rowCount(),3)
        self.assertEqual(pagina.registros[0]['nombre'], 'SIETE')
        self.assertTrue(pagina.tabla.item(0, 5).text().startswith('Urgente'))
        self.assertTrue(pagina.tabla.item(0, 5).font().bold())
        self.assertFalse(pagina.tabla.item(1, 5).font().bold())
        pagina.dias.setValue(91)
        self.assertEqual(pagina.tabla.rowCount(),4)
        pagina.busqueda.setText('No existe'); self.pulsar(pagina,'Actualizar')
        self.assertEqual(pagina.tabla.rowCount(),0)
        self.aviso.assert_not_called()

    def test_07_encuestas(self):
        from encuestas import Encuestas,registrar_encuesta,listar_encuestas
        self.interfaz()
        pagina=Encuestas(self.empleado); pagina.recargar()
        def alta(form):
            self.assertEqual(form.calificacion.checkedId(), -1)
            form.btn_guardar.click()
            self.aviso.assert_called_once()
            self.aviso.reset_mock()
            for numero in range(1, 6):
                cara = form.calificacion.button(numero)
                self.assertFalse(cara.icon().isNull())
                cara.click()
                self.assertEqual(form.calificacion.checkedId(), numero)
                self.assertEqual(sum(b.isChecked() for b in form.calificacion.buttons()), 1)
            form.comentario.setPlainText('Buena atención')
            form.btn_guardar.click()
        self.modal(pagina,'Registrar encuesta',alta)
        self.assertEqual(pagina.tabla.rowCount(),1)
        self.assertIn('5.00 / 5',pagina.resumen.text())
        registro = listar_encuestas(self.empleado)[0]
        folio = f"#{registro['idEncuesta']} · {registro['fecha']:%d/%m/%Y %H:%M:%S}"
        self.assertIn(folio, pagina.resumen.text())
        self.assertEqual(pagina.tabla.item(0, 0).text(), folio)
        self.assertEqual(listar_encuestas(self.empleado, folio), [registro])
        pagina.tabla.selectRow(0)
        def consultar(form):
            self.assertEqual(form.folio, folio)
            self.assertEqual(form.calificacion.checkedId(), 5)
            self.assertFalse(form.calificacion.checkedButton().isEnabled())
            self.assertEqual(form.comentario.toPlainText(), 'Buena atención')
            self.assertTrue(form.comentario.isReadOnly())
        self.modal(pagina,'Consultar',consultar)
        with self.assertRaises(ValueError): registrar_encuesta(self.admin,0,'')
        with self.assertRaises(ValueError): registrar_encuesta(self.admin,5,'x'*501)
        vid=self.sql('INSERT INTO ventas (idUsuario,metodoPago,subtotal,total) VALUES (%s,\'EFECTIVO\',0,0)',(self.admin['idUsuario'],))
        with self.assertRaises(ValueError): registrar_encuesta(self.empleado,4,'',vid)
        registrar_encuesta(self.admin,4,'Encuesta de administrador',vid)
        self.assertEqual(len(listar_encuestas(self.empleado)),1)
        self.assertEqual(len(listar_encuestas(self.admin)),2)
        pagina.calificacion.setCurrentIndex(1)
        self.assertEqual(pagina.tabla.rowCount(),0)
        self.aviso.assert_not_called()

    def test_08_reportes(self):
        from datetime import date
        from decimal import Decimal
        from tempfile import TemporaryDirectory
        from pathlib import Path
        import csv
        from reportes import Reportes,generar_reporte,exportar_csv,TIPOS
        self.interfaz()
        self.sql('INSERT INTO ventas (idUsuario,metodoPago,fecha,subtotal,total) VALUES (%s,\'EFECTIVO\',\'2026-10-01 23:59:59\',12.30,12.30)',(self.empleado['idUsuario'],))
        self.sql('INSERT INTO ventas (idUsuario,metodoPago,fecha,subtotal,total) VALUES (%s,\'TARJETA\',\'2026-10-02 00:00:00\',20,20)',(self.admin['idUsuario'],))
        a,b=date(2026,10,1),date(2026,10,1)
        cols,filas=generar_reporte(self.admin,'Ventas',a,b)
        self.assertEqual(len(filas),1); self.assertEqual(filas[0][-1],Decimal('12.30'))
        _,filas=generar_reporte(self.admin,'Ventas por usuario',a,b,self.empleado['idUsuario'])
        self.assertEqual(filas[0][2],1)
        with self.assertRaises(ValueError): generar_reporte(self.empleado,'Empleados',a,b)
        with self.assertRaises(ValueError): generar_reporte(self.admin,'Ventas',date(2026,11,1),a)
        for tipo in TIPOS:
            columnas,filas=generar_reporte(self.admin,tipo,a,b)
            for fila in filas: self.assertEqual(len(columnas),len(fila),tipo)
        pagina=Reportes(self.admin); pagina.preparar()
        pagina.tipo.setCurrentText('Inventario'); self.pulsar(pagina,'Generar reporte')
        self.assertEqual(pagina.tabla.rowCount(),1)
        with TemporaryDirectory() as carpeta:
            ruta=Path(carpeta)/'reporte.csv'
            with patch('reportes.QFileDialog.getSaveFileName',return_value=(str(ruta),'CSV')), patch.object(QMessageBox,'information'):
                self.pulsar(pagina,'Exportar CSV')
            with ruta.open(encoding='utf-8-sig',newline='') as f: datos=list(csv.reader(f,delimiter=';'))
            self.assertEqual(len(datos),2)
            self.assertEqual(len(datos[0]),len(datos[1]))
            exportar_csv(ruta,['Nombre'],[['=SUM(1,2)']])
            self.assertIn("'=SUM",ruta.read_text(encoding='utf-8-sig'))
        self.aviso.assert_not_called()

    def test_login_empleado_y_exportacion_de_reportes_propios(self):
        import csv
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from login import Login
        import servicios

        self.interfaz()
        eid = servicios.guardar_empleado(self.admin, self.datos, self.cuenta)
        cuenta = servicios.consultar_empleado(self.admin, eid)
        propia = self.sql("""INSERT INTO ventas (idUsuario,metodoPago,subtotal,total)
                             VALUES (%s,'EFECTIVO',12.30,12.30)""", (cuenta['idUsuario'],))
        self.sql("""INSERT INTO ventas (idUsuario,metodoPago,subtotal,total)
                    VALUES (%s,'TARJETA',20,20)""", (self.admin['idUsuario'],))
        with patch('login.conectar', self.conectar_pruebas), \
             patch('mapa.conectar', self.conectar_pruebas), \
             patch('inventario.conectar', self.conectar_pruebas), \
             patch('medicamentos.conectar', self.conectar_pruebas), \
             patch.object(QMessageBox, 'critical') as error:
            login = Login()
            self.addCleanup(login.close)
            login.txt_usuario.setText(self.cuenta['usuario'])
            login.txt_contrasena.setText(self.cuenta['contrasena'])
            login.iniciar_sesion()
            ventana = login.ventana_principal
            self.assertIsNotNone(ventana)
            self.addCleanup(ventana.close)
            self.addCleanup(ventana.pagina_buscar.detener_parpadeo)
            self.assertEqual(ventana.usuario['idUsuario'], cuenta['idUsuario'])
            self.assertEqual(ventana.usuario['rol'], 'EMPLEADO')
            self.assertTrue(ventana.btn_empleados.isHidden())
            self.assertFalse(ventana.btn_reportes.isHidden())
            ventana.btn_ventas.click()
            self.assertEqual([r['idVenta'] for r in ventana.pagina_ventas.registros], [propia])
            self.assertTrue(ventana.pagina_ventas.btn_nueva.isHidden())
            self.assertFalse(ventana.pagina_ventas.btn_nueva.isEnabled())
            ventana.btn_reportes.click()
            pagina = ventana.pagina_reportes
            self.assertIs(ventana.paginas.currentWidget(), pagina)
            self.assertEqual([pagina.tipo.itemText(i) for i in range(pagina.tipo.count())],
                             ['Ventas', 'Ventas por usuario'])
            self.assertEqual(pagina.vendedor.count(), 1)
            self.assertEqual(pagina.vendedor.currentData(), cuenta['idUsuario'])
            self.assertFalse(pagina.vendedor.isEnabled())
            self.assertEqual(pagina.tabla.rowCount(), 1)
            self.assertEqual(pagina.tabla.item(0, 0).text(), str(propia))
            with TemporaryDirectory() as carpeta:
                ruta = Path(carpeta) / 'mis_ventas.csv'
                with patch('reportes.QFileDialog.getSaveFileName', return_value=(str(ruta), 'CSV')), \
                     patch.object(QMessageBox, 'information'):
                    self.pulsar(pagina, 'Exportar CSV')
                with ruta.open(encoding='utf-8-sig', newline='') as archivo:
                    filas = list(csv.reader(archivo, delimiter=';'))
                self.assertEqual(len(filas), 2)
                self.assertEqual(filas[1][0], str(propia))
                self.assertEqual(filas[1][2], self.datos['nombre'])
            pagina.tipo.setCurrentText('Ventas por usuario')
            self.pulsar(pagina, 'Generar reporte')
            self.assertEqual(pagina.tabla.rowCount(), 1)
            self.assertEqual(pagina.tabla.item(0, 0).text(), str(cuenta['idUsuario']))
            self.assertFalse(pagina.vendedor.isEnabled())
            error.assert_not_called()
            self.aviso.assert_not_called()

    def test_interfaz_empleado_bloquea_acciones_de_escritura(self):
        from PyQt6.QtWidgets import QDialog
        from principal import Principal
        from empleados import DialogoEmpleado
        from ventas import DialogoVenta

        self.interfaz()
        with patch('mapa.conectar', self.conectar_pruebas), \
             patch('inventario.conectar', self.conectar_pruebas), \
             patch('medicamentos.conectar', self.conectar_pruebas), \
             patch.object(QDialog, 'exec') as modal, \
             patch.object(QMessageBox, 'question') as confirmacion:
            ventana = Principal(self.empleado)
            self.addCleanup(ventana.close)
            self.addCleanup(ventana.pagina_buscar.detener_parpadeo)
            ventana.btn_medicamentos.click()
            medicamentos = ventana.pagina_medicamentos
            self.assertGreater(medicamentos.tabla.rowCount(), 0)
            medicamentos.tabla.selectRow(0)
            for control in (medicamentos.btn_guardar, medicamentos.btn_modificar,
                            medicamentos.btn_desactivar, medicamentos.btn_reactivar):
                self.assertTrue(control.isHidden())
                self.assertFalse(control.isEnabled())
            medicamentos.abrir_alta()
            medicamentos.tabla.cellDoubleClicked.emit(0, 0)
            ventana.btn_inventario.click()
            inventario = ventana.pagina_inventario
            inventario.seleccionar_medicamento(0, 0)
            self.assertTrue(inventario.panel_movimiento.isHidden())
            self.assertFalse(inventario.btn_registrar.isEnabled())
            inventario.registrar_movimiento()
            ventana.pagina_ventas.nueva()
            ventana.pagina_empleados.nuevo()
            with self.assertRaisesRegex(ValueError, 'administrador'):
                DialogoEmpleado(self.empleado)
            with self.assertRaisesRegex(ValueError, 'administrador'):
                DialogoVenta(self.empleado)
            modal.assert_not_called()
            confirmacion.assert_not_called()
            self.assertEqual(self.aviso.call_count, 5)
            self.assertEqual(self.fallos, [])

    def test_medicamentos_valida_rol_vigente_en_cada_escritura(self):
        from medicamentos import Medicamentos

        self.interfaz()
        with patch('medicamentos.conectar', self.conectar_pruebas), \
             patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes), \
             patch.object(QMessageBox, 'information') as informacion, \
             patch.object(QMessageBox, 'critical') as error:
            pagina = Medicamentos(self.admin)
            self.addCleanup(pagina.close)
            self.addCleanup(pagina.dialogo.close)
            pagina.tabla.selectRow(0)
            pagina.seleccionar_medicamento(0, 0)
            pagina.txt_nombre.setText('Cambio prohibido')
            anterior = self.sql('SELECT * FROM medicamentos', filas=True)
            # La ventana conserva la sesión anterior mientras cambia el rol en la base.
            self.sql("UPDATE usuarios SET rol='EMPLEADO' WHERE idUsuario=%s", (self.admin['idUsuario'],))
            for operacion in (pagina.guardar_medicamento, pagina.modificar_medicamento,
                              pagina.desactivar_medicamento, pagina.reactivar_medicamento):
                with self.subTest(operacion=operacion.__name__):
                    pagina.estado_medicamento_seleccionado = operacion != pagina.reactivar_medicamento
                    self.aviso.reset_mock()
                    operacion()
                    self.aviso.assert_called_once()
                    self.assertIn('administrador', self.aviso.call_args.args[2])
                    self.assertEqual(self.sql('SELECT * FROM medicamentos', filas=True), anterior)
            informacion.assert_not_called()
            error.assert_not_called()

    def test_menu_y_reportes_activos(self):
        from principal import Principal
        from reportes import TIPOS
        self.interfaz()
        with patch('mapa.conectar',self.conectar_pruebas), patch('inventario.conectar',self.conectar_pruebas), patch('medicamentos.conectar',self.conectar_pruebas):
            ventana = Principal(self.admin)
            nombres = [b.text() for b in ventana.botones_menu]
            for retirado in ('Compras', 'Proveedores', 'Categorías', 'Lotes y caducidades'):
                self.assertNotIn(retirado, nombres)
            ventana.btn_alertas.click()
            self.assertIs(ventana.paginas.currentWidget(), ventana.pagina_alertas)
            ventana.btn_reportes.click()
            self.assertNotIn('Compras', TIPOS)
            ventana.pagina_reportes.tipo.setCurrentText('Inventario')
            self.pulsar(ventana.pagina_reportes, 'Generar reporte')
            encabezados = [ventana.pagina_reportes.tabla.horizontalHeaderItem(i).text()
                          for i in range(ventana.pagina_reportes.tabla.columnCount())]
            self.assertIn('Lote', encabezados)
            self.assertIn('Caducidad', encabezados)
            self.assertNotIn('Categoría', encabezados)
            ventana.show()
            for ancho in (1024, 1366):
                ventana.resize(ancho, 768)
                for boton, tabla in [(ventana.btn_medicamentos, ventana.pagina_medicamentos.tabla),
                                     (ventana.btn_reportes, ventana.pagina_reportes.tabla)]:
                    boton.click()
                    self.app.processEvents()
                    self.assertEqual(ventana.width(), ancho)
                    self.assertEqual(tabla.horizontalHeader().length(), tabla.viewport().width())
            ventana.close()
        self.assertEqual(self.fallos, [])
        self.aviso.assert_not_called()
