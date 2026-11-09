"""Componentes compartidos que conservan la paleta y tipografía del sistema."""
from functools import wraps
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView, QMessageBox, QFrame, QHBoxLayout, QVBoxLayout,
                             QWidget, QScrollArea)
from estilos import (ESTILO_TABLA, ESTILO_TITULO_PAGINA, ESTILO_BOTON_SECUNDARIO,
                     ESTILO_DESCRIPCION_PAGINA)
from iconos import icono, imagen_logo


def configurar_pantalla_completa(ventana):
    def alternar():
        if ventana.isFullScreen():
            ventana.showNormal()
        else:
            ventana.showFullScreen()

    QShortcut(QKeySequence('F11'), ventana).activated.connect(alternar)


def manejar_errores(funcion):
    @wraps(funcion)
    def ejecutar(self, *args, **kwargs):
        try:
            return funcion(self, *args, **kwargs)
        except ValueError as exc:
            QMessageBox.warning(self, 'No se pudo completar', str(exc))
    return ejecutar


def titulo(texto):
    label = QLabel(texto)
    label.setStyleSheet(ESTILO_TITULO_PAGINA)
    return label


def logo_farmacia(ancho, alto, *, solo_simbolo=False):
    imagen = QLabel()
    imagen.setObjectName('simboloMenu' if solo_simbolo else 'logoFarmacia')
    imagen.setAccessibleName('Logotipo de Farmacia')
    imagen.setFixedSize(ancho, alto)
    imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
    imagen.setPixmap(imagen_logo(QSize(ancho - 8, alto - 8), solo_simbolo))
    return imagen


def insignia(clave, *, lado=44, dibujo=24):
    imagen = QLabel()
    imagen.setObjectName('insignia')
    imagen.setFixedSize(lado, lado)
    imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
    imagen.setPixmap(icono(clave, '#0064C9', dibujo).pixmap(QSize(dibujo, dibujo), 2))
    return imagen


def encabezado(etiqueta, descripcion, clave):
    fila = QHBoxLayout()
    fila.setSpacing(12)
    fila.addWidget(insignia(clave))
    textos = QVBoxLayout()
    textos.setSpacing(1)
    etiqueta.setStyleSheet(ESTILO_TITULO_PAGINA)
    descripcion.setStyleSheet(ESTILO_DESCRIPCION_PAGINA)
    descripcion.setWordWrap(True)
    textos.addWidget(etiqueta)
    textos.addWidget(descripcion)
    fila.addLayout(textos, 1)
    return fila


def tarjeta(*filas):
    panel = QFrame()
    panel.setObjectName('tarjeta')
    contenido = QVBoxLayout(panel)
    contenido.setContentsMargins(14, 10, 14, 10)
    contenido.setSpacing(8)
    for fila in filas:
        contenido.addLayout(fila)
    return panel


def dimensionar_dialogo(ventana, ancho, alto):
    area = ventana.screen().availableGeometry()
    ventana.resize(min(ancho, area.width() - 32), min(alto, area.height() - 56))


def contenido_desplazable(exterior):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    contenido = QWidget()
    contenido.setObjectName('superficie')
    layout = QVBoxLayout(contenido)
    layout.setContentsMargins(0, 0, 0, 0)
    scroll.setWidget(contenido)
    exterior.addWidget(scroll, 1)
    return layout


def boton(texto, accion, secundario=False):
    widget = QPushButton(texto)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.setAutoDefault(False)
    # clicked emite un bool incluso para botones no marcables. Los decoradores
    # con *args impiden que PyQt descarte ese argumento según la firma original.
    # Estas acciones no usan el estado checked: invocarlas sin argumentos.
    widget.clicked.connect(lambda _checked=False: accion())
    if secundario:
        widget.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
    return widget


class TablaAdaptable(QTableWidget):
    """Distribuye las columnas según el espacio disponible en la tabla."""

    columnas_descriptivas = {
        'Nombre', 'Medicamento', 'Presentación', 'Principio activo', 'Fabricante',
        'Ubicación', 'Vendedor', 'Tipo', 'Detalle', 'Comentario', 'Folio de encuesta',
    }

    def setHorizontalHeaderLabels(self, etiquetas):
        super().setHorizontalHeaderLabels(etiquetas)
        for i, texto in enumerate(etiquetas):
            self.horizontalHeaderItem(i).setToolTip(texto)
        self.ajustar_columnas()

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.ajustar_columnas()

    def ajustar_columnas(self):
        cabecera = self.horizontalHeader()
        minimos = []
        pesos = []
        for i in range(self.columnCount()):
            etiqueta = self.horizontalHeaderItem(i)
            if etiqueta is None:
                return
            minimos.append(cabecera.sectionSizeHint(i))
            pesos.append(3 if etiqueta.text() in self.columnas_descriptivas else 1)

        disponible = self.viewport().width()
        if disponible < sum(minimos):
            # En paneles estrechos, compactar primero los encabezados largos.
            compacto = max(cabecera.minimumSectionSize(), self.fontMetrics().horizontalAdvance('00000'))
            pesos = [max(1, ancho - compacto) for ancho in minimos]
            minimos = [min(ancho, compacto) for ancho in minimos]

        libre = max(0, disponible - sum(minimos))
        peso_total = sum(pesos)
        for i, (minimo, peso) in enumerate(zip(minimos, pesos)):
            extra = libre * peso // peso_total
            cabecera.resizeSection(i, minimo + extra)
            libre -= extra
            peso_total -= peso

    def setItem(self, fila, columna, item):
        if not item.toolTip():
            item.setToolTip(item.text())
        super().setItem(fila, columna, item)


def tabla(columnas):
    widget = TablaAdaptable(0, len(columnas))
    widget.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    widget.setHorizontalHeaderLabels(columnas)
    widget.setStyleSheet(ESTILO_TABLA)
    widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    widget.verticalHeader().hide()
    widget.verticalHeader().setDefaultSectionSize(36)
    widget.setWordWrap(False)
    widget.setShowGrid(False)
    widget.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    return widget


def llenar_tabla(widget, filas):
    widget.setRowCount(0)
    widget.setRowCount(len(filas))
    for fila, valores in enumerate(filas):
        for columna, valor in enumerate(valores):
            item = QTableWidgetItem('' if valor is None else str(valor))
            widget.setItem(fila, columna, item)


def confirmar(parent, titulo_dialogo, mensaje):
    return QMessageBox.question(parent, titulo_dialogo, mensaje,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes


def dinero(valor):
    return f'$ {valor:,.2f}'
