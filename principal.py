# principal.py

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QStackedWidget,
    QMessageBox,
    QScrollArea,
    QSizePolicy
)

from PyQt6.QtCore import Qt, QTimer, QSize, QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtSvg import QSvgRenderer

from estilos import (
    ESTILO_GENERAL,
    FONDO_LOGO_PORTADA,
    ESTILO_LINEA_MENU,
    ESTILO_MENU_LATERAL,
    ESTILO_TITULO_MENU,
    ESTILO_NOMBRE_USUARIO_MENU,
    ESTILO_ROL_USUARIO_MENU,
    ESTILO_BOTON_MENU,
    ESTILO_BOTON_MENU_ACTIVO,
    ESTILO_BOTON_CERRAR,
    ESTILO_CONTENEDOR_PAGINAS
)

from medicamentos import Medicamentos
from inventario import Inventario
from mapa import MapaMedicamentos
from ventas import Ventas
from empleados import Empleados
from alertas import Alertas, obtener_alertas
from reportes import Reportes
from encuestas import Encuestas
from ui_comun import configurar_pantalla_completa, insignia, logo_farmacia, tarjeta
from iconos import icono, imagen_logo


class CabeceraInicio(QFrame):
    def __init__(self, titulo, descripcion):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.ondas = QSvgRenderer(str(Path(__file__).with_name('recursos') / 'ondas-inicio.svg'))
        self.ondas.setAspectRatioMode(Qt.AspectRatioMode.IgnoreAspectRatio)
        self.fila = QHBoxLayout(self)
        bloque_texto = QWidget()
        textos = QVBoxLayout(bloque_texto)
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)
        textos.addStretch(3)
        self.titulo = QLabel(titulo)
        self.titulo.setObjectName('tituloPortada')
        textos.addWidget(self.titulo)
        self.descripcion = QLabel(descripcion)
        self.descripcion.setObjectName('bienvenida')
        self.descripcion.setWordWrap(True)
        textos.addWidget(self.descripcion)
        textos.addSpacing(14)
        self.filete = QFrame()
        self.filete.setObjectName('filetePortada')
        self.filete.setFixedHeight(2)
        textos.addWidget(self.filete, alignment=Qt.AlignmentFlag.AlignLeft)
        textos.addStretch(2)
        self.fila.addWidget(bloque_texto, 1)
        self.marca = QLabel()
        self.marca.setObjectName('marcaPortada')
        self.marca.setAccessibleName('Logotipo de Farmacia')
        self.marca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original = imagen_logo(QSize(260, 216), fondo=FONDO_LOGO_PORTADA)
        self.fila.addWidget(self.marca)
        self.ajustar(640)

    def ajustar(self, ancho):
        alto = max(162, min(338, round(ancho * 0.237)))
        self.setFixedHeight(alto)
        margen = max(16, min(40, ancho // 35))
        self.fila.setContentsMargins(margen, 8, max(12, margen * 2 // 3), 8)
        self.titulo.setStyleSheet(f'font-size: {max(30, round(alto * 0.167))}px;')
        self.descripcion.setStyleSheet(f'font-size: {max(15, round(alto * 0.079))}px;')
        self.filete.setFixedWidth(min(250, ancho // 5))
        placa = max(120, min(320, round(ancho * 0.225)))
        self.marca.setFixedSize(placa, round(placa * 0.695))
        alto_logo = self.marca.height() - 16
        self.marca.setPixmap(self.original.scaled(
            placa * 2, alto_logo * 2, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if evento.size().width() != evento.oldSize().width():
            self.ajustar(evento.size().width())

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = QRectF(self.rect())
        borde = QPainterPath()
        borde.addRoundedRect(area, 20, 20)
        pintor.setClipPath(borde)
        self.ondas.render(pintor, area)


class Principal(QMainWindow):

    def __init__(self, usuario):
        super().__init__()

        self.usuario = usuario

        self.botones_menu = []

        self.setWindowTitle(
            "Sistema de Farmacia"
        )

        self.resize(
            1200,
            700
        )

        self.crear_interfaz()
        configurar_pantalla_completa(self)


    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        contenedor = QWidget()
        contenedor.setObjectName("superficie")

        contenedor.setStyleSheet(
            ESTILO_GENERAL
        )

        self.setCentralWidget(
            contenedor
        )


        layout_principal = QHBoxLayout(
            contenedor
        )

        layout_principal.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout_principal.setSpacing(
            0
        )


        # =====================================================
        # MENÚ LATERAL
        # =====================================================

        menu = QFrame()

        menu.setObjectName(
            "menuLateral"
        )

        menu.setStyleSheet(
            ESTILO_MENU_LATERAL
        )


        layout_menu = QVBoxLayout(
            menu
        )

        layout_menu.setContentsMargins(
            12,
            18,
            12,
            12
        )

        layout_menu.setSpacing(
            4
        )


        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = QLabel("Farmacia")

        titulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        titulo.setStyleSheet(
            ESTILO_TITULO_MENU
        )


        # =====================================================
        # USUARIO
        # =====================================================

        nombre_usuario = QLabel(
            self.usuario["nombre"]
        )

        nombre_usuario.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        nombre_usuario.setStyleSheet(
            ESTILO_NOMBRE_USUARIO_MENU
        )


        rol_usuario = QLabel(
            self.usuario["rol"]
        )

        rol_usuario.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        rol_usuario.setStyleSheet(
            ESTILO_ROL_USUARIO_MENU
        )


        # =====================================================
        # BOTONES DEL MENÚ
        # =====================================================

        self.btn_inicio = self.crear_boton_menu(
            "Inicio"
        )

        self.btn_buscar = self.crear_boton_menu(
            "Buscar medicamento"
        )

        self.btn_medicamentos = self.crear_boton_menu(
            "Medicamentos"
        )

        self.btn_ventas = self.crear_boton_menu(
            "Ventas"
        )

        self.btn_inventario = self.crear_boton_menu(
            "Inventario"
        )

        self.btn_empleados = self.crear_boton_menu(
            "Empleados"
        )

        self.btn_reportes = self.crear_boton_menu(
            "Reportes"
        )

        self.btn_encuestas = self.crear_boton_menu(
            "Encuestas"
        )


        # =====================================================
        # CERRAR SESIÓN
        # =====================================================

        self.btn_cerrar = QPushButton(
            "Cerrar sesión"
        )

        self.btn_cerrar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_cerrar.setMinimumHeight(42)

        self.btn_cerrar.setStyleSheet(
            ESTILO_BOTON_CERRAR
        )


        # =====================================================
        # AGREGAR AL MENÚ
        # =====================================================

        marca = QVBoxLayout()
        marca.setSpacing(0)
        marca.addWidget(logo_farmacia(82, 58, solo_simbolo=True),
                        alignment=Qt.AlignmentFlag.AlignHCenter)
        marca.addWidget(titulo)
        lema = QLabel("— Tu salud, nuestra prioridad —")
        lema.setObjectName("lemaMenu")
        lema.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marca.addWidget(lema)
        layout_menu.addLayout(marca)
        layout_menu.addSpacing(18)

        layout_menu.addWidget(
            self.btn_inicio
        )

        layout_menu.addWidget(
            self.btn_buscar
        )

        layout_menu.addWidget(
            self.btn_medicamentos
        )

        layout_menu.addWidget(
            self.btn_ventas
        )

        layout_menu.addWidget(
            self.btn_inventario
        )

        layout_menu.addWidget(
            self.btn_empleados
        )

        layout_menu.addWidget(
            self.btn_reportes
        )

        layout_menu.addWidget(
            self.btn_encuestas
        )

        self.btn_alertas = self.crear_boton_menu("Alertas")
        layout_menu.addWidget(self.btn_alertas)
        self.btn_alertas.clicked.connect(self.abrir_alertas)

        layout_menu.addStretch()
        linea = QFrame()
        linea.setFixedHeight(1)
        linea.setStyleSheet(ESTILO_LINEA_MENU)
        layout_menu.addWidget(linea)
        perfil = QHBoxLayout()
        perfil.setContentsMargins(6, 8, 4, 3)
        avatar = QLabel()
        avatar.setPixmap(icono("Perfil").pixmap(QSize(22, 22), 2))
        perfil.addWidget(avatar)
        cuenta = QVBoxLayout()
        cuenta.setSpacing(0)
        nombre_usuario.setAlignment(Qt.AlignmentFlag.AlignLeft)
        nombre_usuario.setWordWrap(True)
        rol_usuario.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cuenta.addWidget(nombre_usuario)
        cuenta.addWidget(rol_usuario)
        perfil.addLayout(cuenta, 1)
        layout_menu.addLayout(perfil)
        self.btn_cerrar.setIcon(icono("Cerrar sesión"))

        layout_menu.addWidget(
            self.btn_cerrar
        )


        # =====================================================
        # CONTENEDOR DE PÁGINAS
        # =====================================================

        self.paginas = QStackedWidget()

        self.paginas.setStyleSheet(
            ESTILO_CONTENEDOR_PAGINAS
        )


        # =====================================================
        # INICIO
        # =====================================================

        self.pagina_inicio = self.crear_pagina(
            "Inicio",
            "Bienvenido al Sistema de Farmacia."
        )


        # =====================================================
        # MAPA
        # =====================================================

        self.pagina_buscar = MapaMedicamentos()


        # =====================================================
        # MEDICAMENTOS
        # =====================================================

        self.pagina_medicamentos = Medicamentos()


        # =====================================================
        # VENTAS
        # =====================================================

        self.pagina_ventas = Ventas(self.usuario)


        # =====================================================
        # INVENTARIO
        # =====================================================

        self.pagina_inventario = Inventario(
            self.usuario
        )


        # =====================================================
        # EMPLEADOS
        # =====================================================

        self.pagina_empleados = Empleados(self.usuario)
        self.pagina_ventas.venta_registrada.connect(self.pagina_inventario.cargar_inventario)


        # =====================================================
        # REPORTES
        # =====================================================

        self.pagina_reportes = Reportes(self.usuario)


        # =====================================================
        # ENCUESTAS
        # =====================================================

        self.pagina_encuestas = Encuestas(self.usuario)
        self.pagina_alertas = Alertas(self.usuario)
        self.paginas.addWidget(self.pagina_alertas)
        self.contenedores = {}
        for pagina in [self.pagina_buscar, self.pagina_medicamentos, self.pagina_inventario]:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(pagina)
            self.contenedores[pagina] = scroll
        self.aviso_alertas = QLabel('Consultando alertas...')
        self.aviso_alertas.setWordWrap(True)
        self.aviso_alertas.setObjectName('conteoInicio')
        abrir_alertas = QPushButton('Consultar alertas')
        abrir_alertas.setObjectName('consultarAlertas')
        abrir_alertas.setIcon(icono('Buscar medicamento', '#FFFFFF'))
        abrir_alertas.setIconSize(QSize(20, 20))
        abrir_alertas.clicked.connect(self.abrir_alertas)
        barra = QHBoxLayout()
        seccion = QLabel('Alertas de inventario y caducidad')
        seccion.setObjectName('tituloAlertasInicio')
        seccion.setWordWrap(True)
        campana = QLabel()
        campana.setPixmap(icono('Alertas', '#0064C9', 24).pixmap(QSize(24, 24), 2))
        barra.addWidget(campana)
        barra.addWidget(seccion, 1)
        barra.addWidget(abrir_alertas)
        cuadro = tarjeta(barra)
        cuadro.setObjectName('panelAlertasInicio')
        sombra = QGraphicsDropShadowEffect(cuadro)
        sombra.setColor(QColor(24, 66, 117, 32))
        sombra.setBlurRadius(9)
        sombra.setOffset(0, 2)
        cuadro.setGraphicsEffect(sombra)
        cuadro.layout().setContentsMargins(24, 20, 24, 24)
        cuadro.layout().addWidget(self.aviso_alertas)
        indicadores = QGridLayout()
        indicadores.setHorizontalSpacing(20)
        indicadores.setVerticalSpacing(14)
        indicadores.setColumnStretch(0, 1)
        indicadores.setColumnStretch(1, 1)
        self.indicadores = {}
        tipos = [('Existencia baja', 'Inventario'), ('Próxima caducidad', 'Calendario'),
                 ('Caducado / vence hoy', 'Alertas'), ('Sin caducidad registrada', 'Calendario')]
        for indice, (tipo, simbolo) in enumerate(tipos):
            dato = QFrame()
            dato.setObjectName('indicador')
            fila = QHBoxLayout(dato)
            fila.setContentsMargins(12, 9, 16, 9)
            fila.setSpacing(12)
            distintivo = insignia(simbolo, lado=52, dibujo=28)
            distintivo.setObjectName('iconoIndicador')
            fila.addWidget(distintivo)
            etiqueta = QLabel(tipo)
            etiqueta.setObjectName('nombreIndicador')
            etiqueta.setWordWrap(True)
            fila.addWidget(etiqueta, 1)
            valor = QLabel('—')
            valor.setObjectName('valorIndicador')
            fila.addWidget(valor)
            self.indicadores[tipo] = valor
            indicadores.addWidget(dato, indice // 2, indice % 2)
        cuadro.layout().addLayout(indicadores)
        self.pagina_inicio.layout().insertWidget(1, cuadro)
        self.timer_alertas = QTimer(self)
        self.timer_alertas.setInterval(60000)
        self.timer_alertas.timeout.connect(self.actualizar_alertas)
        self.pagina_alertas.dias.valueChanged.connect(self.actualizar_alertas)
        self.timer_alertas.start()
        self.pagina_ventas.venta_registrada.connect(self.actualizar_alertas)
        self.actualizar_alertas()


        # =====================================================
        # AGREGAR PÁGINAS
        # =====================================================

        self.paginas.addWidget(
            self.pagina_inicio
        )

        self.paginas.addWidget(
            self.contenedores[self.pagina_buscar]
        )

        self.paginas.addWidget(
            self.contenedores[self.pagina_medicamentos]
        )

        self.paginas.addWidget(
            self.pagina_ventas
        )

        self.paginas.addWidget(
            self.contenedores[self.pagina_inventario]
        )

        self.paginas.addWidget(
            self.pagina_empleados
        )

        self.paginas.addWidget(
            self.pagina_reportes
        )

        self.paginas.addWidget(
            self.pagina_encuestas
        )


        # =====================================================
        # CONEXIONES
        # =====================================================

        self.btn_inicio.clicked.connect(
            self.abrir_inicio
        )

        self.btn_buscar.clicked.connect(
            self.abrir_busqueda
        )

        self.btn_medicamentos.clicked.connect(
            self.abrir_medicamentos
        )

        self.btn_ventas.clicked.connect(
            self.abrir_ventas
        )

        self.btn_inventario.clicked.connect(
            self.abrir_inventario
        )

        self.btn_empleados.clicked.connect(
            self.abrir_empleados
        )

        self.btn_reportes.clicked.connect(
            self.abrir_reportes
        )

        self.btn_encuestas.clicked.connect(
            self.abrir_encuestas
        )

        self.btn_cerrar.clicked.connect(
            self.cerrar_sesion
        )


        # =====================================================
        # PERMISOS
        # =====================================================

        self.aplicar_permisos()


        # =====================================================
        # LAYOUT
        # =====================================================

        scroll_menu = QScrollArea()
        scroll_menu.setWidgetResizable(True)
        scroll_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_menu.setFrameShape(QFrame.Shape.NoFrame)
        scroll_menu.setObjectName("scrollMenu")
        scroll_menu.setStyleSheet(ESTILO_MENU_LATERAL)
        scroll_menu.setFixedWidth(211)
        scroll_menu.setWidget(menu)
        layout_principal.addWidget(scroll_menu)

        area_paginas = QScrollArea()
        area_paginas.setWidgetResizable(True)
        area_paginas.setFrameShape(QFrame.Shape.NoFrame)
        area_paginas.setWidget(self.paginas)
        layout_principal.addWidget(area_paginas, 1)


        # =====================================================
        # INICIO
        # =====================================================

        self.paginas.setCurrentWidget(
            self.pagina_inicio
        )

        self.marcar_boton_activo(
            self.btn_inicio
        )


    # =========================================================
    # CREAR BOTÓN DEL MENÚ
    # =========================================================

    def crear_boton_menu(
        self,
        texto
    ):

        boton = QPushButton(
            texto
        )

        boton.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        boton.setMinimumHeight(45)

        boton.setStyleSheet(
            ESTILO_BOTON_MENU
        )

        boton.setIcon(icono(texto))
        boton.setIconSize(QSize(22, 22))
        self.botones_menu.append(
            boton
        )

        return boton

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        compacto = self.height() < 705
        if not hasattr(self, 'btn_cerrar') or compacto == getattr(self, '_menu_compacto', None):
            return
        self._menu_compacto = compacto
        menu = self.btn_cerrar.parentWidget().layout()
        menu.setSpacing(1 if compacto else 4)
        vertical = 7 if compacto else 18
        menu.setContentsMargins(12, vertical, 12, vertical)
        for boton in self.botones_menu + [self.btn_cerrar]:
            boton.setMinimumHeight(34 if compacto else 45)


    # =========================================================
    # MARCAR BOTÓN ACTIVO
    # =========================================================

    def marcar_boton_activo(
        self,
        boton_activo
    ):

        for boton in self.botones_menu:

            boton.setStyleSheet(
                ESTILO_BOTON_MENU
            )


        boton_activo.setStyleSheet(
            ESTILO_BOTON_MENU_ACTIVO
        )


    # =========================================================
    # CREAR PÁGINA TEMPORAL
    # =========================================================

    def crear_pagina(
        self,
        titulo,
        descripcion
    ):

        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)
        layout.addWidget(CabeceraInicio(titulo, descripcion))
        layout.addStretch()
        return pagina


    # =========================================================
    # INICIO
    # =========================================================

    def abrir_inicio(self):
        self.actualizar_alertas()

        self.paginas.setCurrentWidget(
            self.pagina_inicio
        )

        self.marcar_boton_activo(
            self.btn_inicio
        )


    # =========================================================
    # BÚSQUEDA / MAPA
    # =========================================================

    def abrir_busqueda(self):

        self.pagina_buscar.recargar()

        self.paginas.setCurrentWidget(
            self.contenedores[self.pagina_buscar]
        )

        self.marcar_boton_activo(
            self.btn_buscar
        )


    # =========================================================
    # MEDICAMENTOS
    # =========================================================

    def abrir_medicamentos(self):

        self.pagina_medicamentos.cargar_ubicaciones()

        self.pagina_medicamentos.cargar_medicamentos()


        self.paginas.setCurrentWidget(
            self.contenedores[self.pagina_medicamentos]
        )

        self.marcar_boton_activo(
            self.btn_medicamentos
        )


    # =========================================================
    # VENTAS
    # =========================================================

    def abrir_ventas(self):

        self.pagina_ventas.recargar()
        self.paginas.setCurrentWidget(
            self.pagina_ventas
        )

        self.marcar_boton_activo(
            self.btn_ventas
        )


    # =========================================================
    # INVENTARIO
    # =========================================================

    def abrir_inventario(self):

        self.pagina_inventario.cargar_inventario()

        self.paginas.setCurrentWidget(
            self.contenedores[self.pagina_inventario]
        )

        self.marcar_boton_activo(
            self.btn_inventario
        )


    # =========================================================
    # EMPLEADOS
    # =========================================================

    def abrir_empleados(self):

        if self.usuario['rol'] != 'ADMIN':
            QMessageBox.warning(self, 'Acceso denegado', 'Solo el administrador puede gestionar empleados.')
            return
        self.pagina_empleados.recargar()
        self.paginas.setCurrentWidget(
            self.pagina_empleados
        )

        self.marcar_boton_activo(
            self.btn_empleados
        )


    # =========================================================
    # REPORTES
    # =========================================================

    def abrir_reportes(self):
        if self.usuario['rol'] != 'ADMIN':
            QMessageBox.warning(self, 'Acceso denegado', 'Solo el administrador puede consultar reportes.')
            return
        self.pagina_reportes.preparar()

        self.paginas.setCurrentWidget(
            self.pagina_reportes
        )

        self.marcar_boton_activo(
            self.btn_reportes
        )


    # =========================================================
    # ENCUESTAS
    # =========================================================

    def abrir_encuestas(self):
        self.pagina_encuestas.recargar()

        self.paginas.setCurrentWidget(
            self.pagina_encuestas
        )

        self.marcar_boton_activo(
            self.btn_encuestas
        )


    # =========================================================
    # PERMISOS
    # =========================================================

    def aplicar_permisos(self):

        rol = self.usuario["rol"]


        if rol == "EMPLEADO":

            self.btn_empleados.hide()
            self.btn_reportes.hide()


    # =========================================================
    # CERRAR SESIÓN
    # =========================================================

    def cerrar_sesion(self):

        respuesta = QMessageBox.question(
            self,
            "Cerrar sesión",
            "¿Desea cerrar la sesión?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )


        if (
            respuesta
            == QMessageBox.StandardButton.Yes
        ):

            self.pagina_buscar.detener_parpadeo()

            self.close()

    def abrir_alertas(self):
        self.pagina_alertas.recargar()
        self.paginas.setCurrentWidget(self.pagina_alertas)
        self.marcar_boton_activo(self.btn_alertas)

    def actualizar_alertas(self, *_):
        try:
            alertas = obtener_alertas(self.usuario, self.pagina_alertas.dias.value())
            conteo = {}
            for alerta in alertas:
                conteo[alerta['tipo']] = conteo.get(alerta['tipo'], 0) + 1
            for tipo, valor in self.indicadores.items():
                valor.setText(str(conteo.get(tipo, 0)))
            resumen = {0: 'Sin alertas de inventario o caducidad.', 1: '1 alerta registrada'}
            self.aviso_alertas.setText(resumen.get(len(alertas), f'{len(alertas)} alertas registradas'))
            self.btn_alertas.setText(f'Alertas ({len(alertas)})')
            if self.paginas.currentWidget() is self.pagina_alertas:
                self.pagina_alertas.recargar()
        except ValueError:
            for valor in self.indicadores.values():
                valor.setText('—')
            self.aviso_alertas.setText('No se pudieron consultar las alertas. Revise la conexión local.')

    def closeEvent(self, event):
        self.timer_alertas.stop()
        self.pagina_buscar.detener_parpadeo()
        super().closeEvent(event)
