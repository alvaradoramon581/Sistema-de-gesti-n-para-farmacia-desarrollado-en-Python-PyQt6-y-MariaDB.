"""Lista de empleados y operaciones exclusivamente en ventanas modales."""
from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QLabel, QDateEdit, QCheckBox, QScrollArea)
from estilos import ESTILO_GENERAL, ESTILO_BOTON_PELIGRO
import servicios
from ui_comun import (titulo, boton, tabla, llenar_tabla, confirmar, manejar_errores,
                      encabezado, tarjeta, dimensionar_dialogo)


class DialogoEmpleado(QDialog):
    def __init__(self, usuario, empleado=None, consulta=False, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.empleado = empleado or {}
        self.setWindowTitle('Consultar empleado' if consulta else ('Modificar empleado' if empleado else 'Registrar empleado'))
        self.setStyleSheet(ESTILO_GENERAL)
        dimensionar_dialogo(self, 660, 680)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.addWidget(titulo(self.windowTitle()))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenido = tarjeta()
        form = QFormLayout()
        contenido.layout().addLayout(form)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setSpacing(12)
        self.campos = {}
        for clave, etiqueta, longitud in [('nombre','Nombre completo *',100),
                ('rfc','RFC *',13), ('direccion','Dirección *',200),
                ('telefono','Teléfono *',20), ('identificacion','Identificación (folio) *',100)]:
            campo = QLineEdit(str(self.empleado.get(clave) or ''))
            campo.setMaxLength(longitud)
            campo.setReadOnly(consulta)
            self.campos[clave] = campo
            form.addRow(etiqueta, campo)
        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat('dd/MM/yyyy')
        self.fecha.setDateRange(QDate(1900,1,1), QDate.currentDate().addDays(-1))
        self.fecha.setSpecialValueText('Seleccione una fecha')
        valor = self.empleado.get('fechaNacimiento')
        self.fecha.setDate(QDate(valor.year, valor.month, valor.day) if valor else QDate(1900,1,1))
        self.fecha.setEnabled(not consulta)
        form.insertRow(1, 'Fecha de nacimiento *', self.fecha)
        self.con_cuenta = QCheckBox('Cuenta de acceso al sistema')
        self.con_cuenta.setChecked(bool(self.empleado.get('idUsuario')))
        self.con_cuenta.setEnabled(not consulta and not self.empleado.get('idUsuario'))
        form.addRow(self.con_cuenta)
        self.cuenta_panel = QWidget()
        cuenta_form = QFormLayout(self.cuenta_panel)
        cuenta_form.setContentsMargins(0,0,0,0)
        self.nombre_usuario = QLineEdit(self.empleado.get('usuario') or '')
        self.nombre_usuario.setMaxLength(50)
        self.nombre_usuario.setReadOnly(consulta)
        self.rol = QComboBox()
        self.rol.addItems(['EMPLEADO', 'ADMIN'])
        self.rol.setCurrentText(self.empleado.get('rol') or 'EMPLEADO')
        self.rol.setEnabled(not consulta)
        self.clave = QLineEdit()
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.setPlaceholderText('Vacío = conservar contraseña' if self.empleado.get('idUsuario') else 'Mínimo 8 caracteres')
        self.repetir = QLineEdit()
        self.repetir.setEchoMode(QLineEdit.EchoMode.Password)
        cuenta_form.addRow('Usuario *', self.nombre_usuario)
        cuenta_form.addRow('Rol', self.rol)
        if not consulta:
            cuenta_form.addRow('Contraseña', self.clave)
            cuenta_form.addRow('Repetir contraseña', self.repetir)
        form.addRow(self.cuenta_panel)
        self.cuenta_panel.setVisible(self.con_cuenta.isChecked())
        self.con_cuenta.toggled.connect(self.cuenta_panel.setVisible)
        if empleado:
            form.addRow('Estado', QLabel('Activo' if empleado['activo'] else 'Inactivo'))
        scroll.setWidget(contenido)
        layout.addWidget(scroll, 1)
        acciones = QHBoxLayout()
        acciones.addStretch()
        acciones.addWidget(boton('Cerrar' if consulta else 'Cancelar', self.reject, True))
        if not consulta:
            self.btn_guardar = boton('Guardar', self.guardar)
            acciones.addWidget(self.btn_guardar)
        layout.addLayout(acciones)

    @manejar_errores
    def guardar(self):
        datos = {clave: campo.text() for clave, campo in self.campos.items()}
        if self.fecha.date() == self.fecha.minimumDate():
            raise ValueError('Seleccione la fecha de nacimiento.')
        datos['fechaNacimiento'] = self.fecha.date().toPyDate()
        cuenta = None
        if self.con_cuenta.isChecked():
            if self.clave.text() != self.repetir.text():
                raise ValueError('Las contraseñas no coinciden.')
            cuenta = {'usuario': self.nombre_usuario.text().strip(), 'rol': self.rol.currentText(),
                      'contrasena': self.clave.text()}
        servicios.guardar_empleado(self.usuario, datos, cuenta, self.empleado.get('idEmpleado'))
        self.accept()


class Empleados(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.registros = []
        self.setStyleSheet(ESTILO_GENERAL)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24,22,24,20)
        layout.setSpacing(12)
        layout.addLayout(encabezado(titulo('Empleados'), QLabel('Registro y administración de empleados y cuentas de acceso.'), 'Empleados'))
        filtros = QHBoxLayout()
        self.estado = QComboBox()
        for nombre, valor in [('Activos',1),('Inactivos',0),('Todos',None)]:
            self.estado.addItem(nombre, valor)
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText('Buscar por nombre, RFC, teléfono, dirección o usuario...')
        filtros.addWidget(self.estado)
        filtros.addWidget(self.busqueda, 1)
        filtros.addWidget(boton('Actualizar', self.recargar, True))
        layout.addWidget(tarjeta(filtros))
        acciones = QHBoxLayout()
        acciones.addWidget(boton('Registrar empleado', self.nuevo))
        self.btn_consultar = boton('Consultar', self.consultar, True)
        self.btn_editar = boton('Modificar', self.editar, True)
        self.btn_estado = boton('Desactivar', self.cambiar_estado, True)
        self.btn_eliminar = boton('Eliminar', self.eliminar, True)
        self.btn_eliminar.setStyleSheet(ESTILO_BOTON_PELIGRO)
        self.acciones = [self.btn_consultar, self.btn_editar, self.btn_estado, self.btn_eliminar]
        for widget in self.acciones:
            acciones.addWidget(widget)
        acciones.addStretch()
        layout.addLayout(acciones)
        self.tabla = tabla(['ID', 'Nombre', 'RFC', 'Teléfono', 'Usuario', 'Rol', 'Estado'])
        layout.addWidget(self.tabla, 1)
        self.resumen = QLabel('Sin registros cargados.')
        self.resumen.setObjectName("resumen")
        layout.addWidget(self.resumen)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.recargar)
        self.busqueda.textChanged.connect(lambda: self.timer.start())
        self.estado.currentIndexChanged.connect(self.recargar)
        self.tabla.itemSelectionChanged.connect(self.seleccion)
        self.tabla.cellDoubleClicked.connect(self.consultar)
        self.seleccion()

    @manejar_errores
    def recargar(self, *_):
        self.timer.stop()
        self.registros = []
        llenar_tabla(self.tabla, [])
        self.resumen.setText('Sin resultados.')
        self.registros = servicios.listar_empleados(self.usuario, self.busqueda.text(), self.estado.currentData())
        llenar_tabla(self.tabla, [(r['idEmpleado'],r['nombre'],r['rfc'],r['telefono'],
                     r['usuario'] or 'Sin cuenta',r['rol'] or '—','Activo' if r['activo'] else 'Inactivo')
                     for r in self.registros])
        self.resumen.setText(f'{len(self.registros)} empleado(s). Seleccione uno para consultar o modificar.')
        self.seleccion()

    def seleccionado(self):
        fila = self.tabla.currentRow()
        if not self.tabla.selectedItems() or fila < 0 or fila >= len(self.registros):
            raise ValueError('Seleccione un empleado.')
        return self.registros[fila]

    def seleccion(self):
        valido = bool(self.tabla.selectedItems())
        for widget in self.acciones:
            widget.setEnabled(valido)
        if valido:
            self.btn_estado.setText('Desactivar' if self.seleccionado()['activo'] else 'Reactivar')

    @manejar_errores
    def nuevo(self, *_):
        if DialogoEmpleado(self.usuario, parent=self).exec():
            self.recargar()

    @manejar_errores
    def consultar(self, *_):
        empleado = servicios.consultar_empleado(self.usuario, self.seleccionado()['idEmpleado'])
        DialogoEmpleado(self.usuario, empleado, consulta=True, parent=self).exec()

    @manejar_errores
    def editar(self, *_):
        empleado = servicios.consultar_empleado(self.usuario, self.seleccionado()['idEmpleado'])
        if DialogoEmpleado(self.usuario, empleado, parent=self).exec():
            self.recargar()

    @manejar_errores
    def cambiar_estado(self, *_):
        empleado = servicios.consultar_empleado(self.usuario, self.seleccionado()['idEmpleado'])
        accion = 'desactivar' if empleado['activo'] else 'reactivar'
        if confirmar(self, accion.capitalize() + ' empleado',
                     f"¿Desea {accion} a {empleado['nombre']}? También cambiará su acceso al sistema."):
            servicios.cambiar_empleado(self.usuario, empleado['idEmpleado'], accion)
            self.recargar()

    @manejar_errores
    def eliminar(self, *_):
        empleado = self.seleccionado()
        if confirmar(self, 'Eliminar empleado', f"¿Eliminar el expediente de {empleado['nombre']}?\n"
                     'Esta acción es permanente. Su cuenta quedará inactiva y se conservarán sus ventas.\n'
                     'Para conservar el expediente, use Desactivar.'):
            servicios.cambiar_empleado(self.usuario, empleado['idEmpleado'], 'eliminar')
            self.recargar()
