"""Historial de ventas con registro y consulta en ventanas emergentes."""
from decimal import Decimal
from PyQt6.QtCore import QDate, QTimer, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QCheckBox, QInputDialog, QMessageBox)
from estilos import ESTILO_GENERAL, ESTILO_TOTAL
import servicios
from ui_comun import (titulo, boton, tabla, llenar_tabla, confirmar, manejar_errores, dinero,
                      encabezado, tarjeta, dimensionar_dialogo, contenido_desplazable)


class DialogoVenta(QDialog):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.productos = []
        self.carrito = {}
        self.id_venta = None
        self.setWindowTitle('Registrar venta')
        self.setStyleSheet(ESTILO_GENERAL)
        dimensionar_dialogo(self, 1000, 715)
        exterior = QVBoxLayout(self)
        exterior.setContentsMargins(20,16,20,16)
        exterior.setSpacing(9)
        exterior.addLayout(encabezado(titulo('Registrar venta'), QLabel(f"Vendedor: {usuario['nombre']}"), 'Ventas'))
        layout = contenido_desplazable(exterior)
        layout.setSpacing(7)
        busqueda = QHBoxLayout()
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText('Nombre, código de barras, principio activo o fabricante...')
        busqueda.addWidget(self.buscar, 1)
        busqueda.addWidget(boton('Buscar', self.cargar_productos))
        layout.addWidget(tarjeta(busqueda))
        self.resultados = tabla(['Medicamento', 'Presentación', 'Código', 'Existencia', 'Precio', 'Ubicación'])
        layout.addWidget(self.resultados, 1)
        self.info_busqueda = QLabel('')
        agregar = QHBoxLayout()
        agregar.addWidget(self.info_busqueda, 1)
        self.info_busqueda.setWordWrap(True)
        agregar.addWidget(QLabel('Cantidad:'))
        self.cantidad = QSpinBox()
        self.cantidad.setRange(1, 999999)
        agregar.addWidget(self.cantidad)
        agregar.addWidget(boton('Agregar a la venta', self.agregar))
        layout.addLayout(agregar)
        rotulo = QLabel('Productos de la venta')
        rotulo.setObjectName('seccion')
        layout.addWidget(rotulo)
        self.detalle = tabla(['Medicamento', 'Presentación', 'Cantidad', 'Precio unitario', 'Importe'])
        layout.addWidget(self.detalle, 1)
        editar = QHBoxLayout()
        editar.addWidget(boton('Cambiar cantidad', self.cambiar_cantidad, True))
        editar.addWidget(boton('Quitar producto', self.quitar, True))
        editar.addStretch()
        self.total = QLabel('Total: $ 0.00')
        self.total.setStyleSheet(ESTILO_TOTAL)
        editar.addWidget(self.total)
        exterior.addLayout(editar)
        pago = QHBoxLayout()
        pago.addWidget(QLabel('Método de pago:'))
        self.metodo = QComboBox()
        for texto, valor in [('Efectivo','EFECTIVO'),('Tarjeta','TARJETA'),('Transferencia','TRANSFERENCIA')]:
            self.metodo.addItem(texto, valor)
        pago.addWidget(self.metodo)
        pago.addStretch()
        pago.addWidget(boton('Cancelar', self.reject, True))
        self.btn_guardar = boton('Confirmar venta', self.guardar)
        self.btn_guardar.setEnabled(False)
        pago.addWidget(self.btn_guardar)
        exterior.addWidget(tarjeta(pago))
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.cargar_productos)
        self.buscar.textChanged.connect(lambda: self.timer.start())
        self.buscar.returnPressed.connect(self.cargar_productos)
        self.resultados.cellDoubleClicked.connect(self.agregar)
        self.cargar_productos()

    @manejar_errores
    def cargar_productos(self, *_):
        self.timer.stop()
        self.productos = []
        llenar_tabla(self.resultados, [])
        self.productos = servicios.buscar_productos(self.usuario, self.buscar.text())
        llenar_tabla(self.resultados, [(p['nombre'],p['presentacion'],p['codigoBarras'],
            p['cantidad'],dinero(p['precioVenta']),p['ubicacion']) for p in self.productos])
        self.info_busqueda.setText(f'{len(self.productos)} resultado(s). Se muestran hasta 200; refine la búsqueda.')
        if len(self.productos) == 1:
            self.resultados.selectRow(0)

    @manejar_errores
    def agregar(self, *_):
        fila = self.resultados.currentRow()
        if fila < 0 or not self.resultados.selectedItems():
            raise ValueError('Seleccione un medicamento de los resultados.')
        producto = self.productos[fila]
        clave = producto['idMedicamento']
        anterior = self.carrito.get(clave, {}).get('cantidad', 0)
        cantidad = anterior + self.cantidad.value()
        if cantidad > producto['cantidad']:
            raise ValueError(f"Solo hay {producto['cantidad']} unidades disponibles.")
        self.carrito[clave] = {**producto, 'cantidad': cantidad,
                              'existencia': producto['cantidad'], 'precioUnitario': producto['precioVenta']}
        self.actualizar_carrito()
        self.cantidad.setValue(1)

    def actualizar_carrito(self):
        llenar_tabla(self.detalle, [(p['nombre'],p['presentacion'],p['cantidad'],
            dinero(p['precioUnitario']),dinero(p['precioUnitario'] * p['cantidad']))
            for p in self.carrito.values()])
        self.importe = sum((p['precioUnitario'] * p['cantidad'] for p in self.carrito.values()), Decimal('0.00'))
        self.total.setText('Total: ' + dinero(self.importe))
        self.btn_guardar.setEnabled(bool(self.carrito))

    def clave_seleccionada(self):
        fila = self.detalle.currentRow()
        if fila < 0 or not self.detalle.selectedItems():
            raise ValueError('Seleccione un producto de la venta.')
        return list(self.carrito)[fila]

    @manejar_errores
    def cambiar_cantidad(self, *_):
        clave = self.clave_seleccionada()
        producto = self.carrito[clave]
        cantidad, aceptado = QInputDialog.getInt(self, 'Cambiar cantidad', producto['nombre'],
            producto['cantidad'], 1, min(producto['existencia'], 999999))
        if aceptado:
            producto['cantidad'] = cantidad
            self.actualizar_carrito()

    @manejar_errores
    def quitar(self, *_):
        del self.carrito[self.clave_seleccionada()]
        self.actualizar_carrito()

    @manejar_errores
    def guardar(self, *_):
        if self.id_venta is not None:
            return
        if not confirmar(self, 'Confirmar venta',
            f'¿Registrar la venta por {dinero(self.importe)} mediante {self.metodo.currentText().lower()}?'):
            return
        self.btn_guardar.setEnabled(False)
        try:
            self.id_venta, total, alertas = servicios.registrar_venta(
                self.usuario, list(self.carrito.values()), self.metodo.currentData())
        except ValueError:
            self.btn_guardar.setEnabled(True)
            self.cargar_productos()
            raise
        mensaje = f'Venta #{self.id_venta} registrada. Total: {dinero(total)}.'
        if alertas:
            mensaje += '\n\nExistencias bajas:\n' + '\n'.join(alertas)
        QMessageBox.information(self, 'Venta registrada', mensaje)
        self.accept()

    def reject(self):
        if not self.carrito or confirmar(self, 'Cancelar venta', '¿Descartar los productos de esta venta sin guardar?'):
            super().reject()


class DialogoDetalleVenta(QDialog):
    def __init__(self, venta, detalles, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Venta #{venta['idVenta']}")
        self.setStyleSheet(ESTILO_GENERAL)
        dimensionar_dialogo(self, 850, 500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25,20,25,20)
        layout.addWidget(titulo(self.windowTitle()))
        info = QLabel(f"Fecha: {venta['fecha']}   |   Vendedor: {venta['vendedor']}\n"
                      f"Método de pago: {venta['metodoPago']}")
        info.setWordWrap(True)
        layout.addWidget(info)
        productos = tabla(['Medicamento', 'Presentación', 'Cantidad', 'Precio unitario', 'Importe'])
        llenar_tabla(productos, [(p['nombre'],p['presentacion'],p['cantidad'],
            dinero(p['precioUnitario']),dinero(p['subtotal'])) for p in detalles])
        layout.addWidget(productos, 1)
        layout.addWidget(titulo('Total: ' + dinero(venta['total'])))
        layout.addWidget(boton('Cerrar', self.accept))


class Ventas(QWidget):
    venta_registrada = pyqtSignal()

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.registros = []
        self.setStyleSheet(ESTILO_GENERAL)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24,22,24,20)
        layout.setSpacing(12)
        descripcion = QLabel('Historial de ventas.' if usuario['rol']=='ADMIN' else 'Historial de sus ventas.')
        layout.addLayout(encabezado(titulo('Ventas'), descripcion, 'Ventas'))
        filtros = QHBoxLayout()
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText('Buscar por folio o vendedor...')
        filtros.addWidget(self.busqueda, 1)
        filtros.addWidget(boton('Actualizar', self.recargar, True))
        fechas = QHBoxLayout()
        self.filtrar_fecha = QCheckBox('Filtrar por fecha')
        fechas.addWidget(self.filtrar_fecha)
        self.desde = QDateEdit(QDate.currentDate().addMonths(-1))
        self.hasta = QDateEdit(QDate.currentDate())
        for texto, campo in [('Desde',self.desde),('Hasta',self.hasta)]:
            campo.setCalendarPopup(True)
            campo.setDisplayFormat('dd/MM/yyyy')
            campo.setEnabled(False)
            self.filtrar_fecha.toggled.connect(campo.setEnabled)
            fechas.addWidget(QLabel(texto))
            fechas.addWidget(campo)
            campo.dateChanged.connect(self.recargar)
        fechas.addStretch()
        layout.addWidget(tarjeta(filtros, fechas))
        acciones = QHBoxLayout()
        acciones.addWidget(boton('Registrar venta', self.nueva))
        self.btn_consultar = boton('Consultar detalle', self.consultar, True)
        self.btn_consultar.setEnabled(False)
        acciones.addWidget(self.btn_consultar)
        acciones.addStretch()
        layout.addLayout(acciones)
        self.tabla = tabla(['Folio','Fecha','Vendedor','Método de pago','Subtotal','Total'])
        layout.addWidget(self.tabla, 1)
        self.resumen = QLabel('Sin registros cargados.')
        self.resumen.setObjectName("resumen")
        layout.addWidget(self.resumen)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.recargar)
        self.busqueda.textChanged.connect(lambda: self.timer.start())
        self.filtrar_fecha.toggled.connect(self.recargar)
        self.tabla.itemSelectionChanged.connect(lambda: self.btn_consultar.setEnabled(bool(self.tabla.selectedItems())))
        self.tabla.cellDoubleClicked.connect(self.consultar)

    @manejar_errores
    def recargar(self, *_):
        self.timer.stop()
        self.registros = []
        llenar_tabla(self.tabla, [])
        self.resumen.setText('Sin resultados.')
        desde = self.desde.date().toPyDate() if self.filtrar_fecha.isChecked() else None
        hasta = self.hasta.date().toPyDate() if self.filtrar_fecha.isChecked() else None
        if desde and desde > hasta:
            raise ValueError('La fecha inicial no puede ser posterior a la final.')
        self.registros = servicios.listar_ventas(self.usuario, self.busqueda.text(), desde, hasta)
        llenar_tabla(self.tabla, [(v['idVenta'],str(v['fecha']),v['vendedor'],v['metodoPago'],
            dinero(v['subtotal']),dinero(v['total'])) for v in self.registros])
        total = sum((v['total'] for v in self.registros), Decimal('0.00'))
        self.resumen.setText(f'{len(self.registros)} venta(s) en la lista. Total: {dinero(total)}')

    def nueva(self, *_):
        if DialogoVenta(self.usuario, self).exec():
            self.recargar()
            self.venta_registrada.emit()

    @manejar_errores
    def consultar(self, *_):
        fila = self.tabla.currentRow()
        if fila < 0 or not self.tabla.selectedItems():
            raise ValueError('Seleccione una venta.')
        venta, detalles = servicios.consultar_venta(self.usuario, self.registros[fila]['idVenta'])
        DialogoDetalleVenta(venta, detalles, self).exec()
