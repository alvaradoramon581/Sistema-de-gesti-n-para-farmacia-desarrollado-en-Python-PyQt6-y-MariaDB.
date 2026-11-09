"""Base visual de listas y formularios emergentes."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QFormLayout
from estilos import ESTILO_GENERAL
from ui_comun import (titulo, boton, tabla, llenar_tabla, encabezado, tarjeta,
                      dimensionar_dialogo, contenido_desplazable)


class Listado(QWidget):
    def __init__(self, usuario, nombre, columnas, descripcion=''):
        super().__init__()
        self.usuario = usuario
        self.registros = []
        self.setStyleSheet(ESTILO_GENERAL)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24,22,24,20)
        self.layout.setSpacing(12)
        clave = 'Encuestas' if nombre == 'Encuestas de satisfacción' else nombre
        self.layout.addLayout(encabezado(titulo(nombre), QLabel(descripcion), clave))
        self.filtros = QHBoxLayout()
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText('Buscar...')
        self.filtros.addWidget(self.busqueda,1)
        self.filtros.addWidget(boton('Actualizar',self.recargar,True))
        self.busqueda.returnPressed.connect(self.recargar)
        self.panel_filtros = tarjeta(self.filtros)
        self.layout.addWidget(self.panel_filtros)
        self.acciones = QHBoxLayout()
        self.acciones.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(self.acciones)
        self.tabla = tabla(columnas)
        self.layout.addWidget(self.tabla,1)
        self.resumen = QLabel('Pulse Actualizar para consultar.')
        self.resumen.setObjectName("resumen")
        self.resumen.setWordWrap(True)
        self.layout.addWidget(self.resumen)

    def seleccionado(self):
        fila = self.tabla.currentRow()
        if not self.tabla.selectedItems() or not 0 <= fila < len(self.registros):
            raise ValueError('Seleccione un registro de la lista.')
        return self.registros[fila]

    def mostrar(self, registros, filas):
        self.registros = registros
        llenar_tabla(self.tabla, filas)
        self.resumen.setText(f'{len(registros)} registro(s).')

    def limpiar(self):
        self.mostrar([], [])


class Formulario(QDialog):
    def __init__(self, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle(nombre)
        self.setStyleSheet(ESTILO_GENERAL)
        dimensionar_dialogo(self, 620, 450)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25,20,25,20)
        self.layout.addWidget(titulo(nombre))
        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        contenido = contenido_desplazable(self.layout)
        contenido.addWidget(tarjeta(self.form))
        contenido.addStretch()
        self.acciones = QHBoxLayout()
        self.acciones.addStretch()
        self.acciones.addWidget(boton('Cerrar',self.reject,True))
        self.layout.addLayout(self.acciones)

    def guardar_boton(self, accion):
        self.btn_guardar = boton('Guardar',accion)
        self.acciones.addWidget(self.btn_guardar)
