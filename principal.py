# principal.py

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QStackedWidget,
    QMessageBox
)

from PyQt6.QtCore import Qt

from estilos import (
    ESTILO_GENERAL,
    ESTILO_MENU_LATERAL,
    ESTILO_TITULO_MENU,
    ESTILO_NOMBRE_USUARIO_MENU,
    ESTILO_ROL_USUARIO_MENU,
    ESTILO_BOTON_MENU,
    ESTILO_BOTON_MENU_ACTIVO,
    ESTILO_BOTON_CERRAR,
    ESTILO_CONTENEDOR_PAGINAS,
    ESTILO_TITULO_PAGINA,
    ESTILO_DESCRIPCION_PAGINA
)

from medicamentos import Medicamentos
from inventario import Inventario
from mapa import MapaMedicamentos


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


    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        contenedor = QWidget()

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

        menu.setFixedWidth(
            245
        )

        menu.setStyleSheet(
            ESTILO_MENU_LATERAL
        )


        layout_menu = QVBoxLayout(
            menu
        )

        layout_menu.setContentsMargins(
            15,
            20,
            15,
            20
        )

        layout_menu.setSpacing(
            7
        )


        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = QLabel(
            "FARMACIA"
        )

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

        self.btn_cerrar.setMinimumHeight(
            45
        )

        self.btn_cerrar.setStyleSheet(
            ESTILO_BOTON_CERRAR
        )


        # =====================================================
        # AGREGAR AL MENÚ
        # =====================================================

        layout_menu.addWidget(
            titulo
        )

        layout_menu.addWidget(
            nombre_usuario
        )

        layout_menu.addWidget(
            rol_usuario
        )

        layout_menu.addSpacing(
            20
        )

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

        layout_menu.addStretch()

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

        self.pagina_ventas = self.crear_pagina(
            "Ventas",
            "Registro de ventas."
        )


        # =====================================================
        # INVENTARIO
        # =====================================================

        self.pagina_inventario = Inventario(
            self.usuario
        )


        # =====================================================
        # EMPLEADOS
        # =====================================================

        self.pagina_empleados = self.crear_pagina(
            "Empleados",
            "Administración de empleados."
        )


        # =====================================================
        # REPORTES
        # =====================================================

        self.pagina_reportes = self.crear_pagina(
            "Reportes",
            "Reportes generales y por usuario."
        )


        # =====================================================
        # ENCUESTAS
        # =====================================================

        self.pagina_encuestas = self.crear_pagina(
            "Encuestas",
            "Encuestas de satisfacción."
        )


        # =====================================================
        # AGREGAR PÁGINAS
        # =====================================================

        self.paginas.addWidget(
            self.pagina_inicio
        )

        self.paginas.addWidget(
            self.pagina_buscar
        )

        self.paginas.addWidget(
            self.pagina_medicamentos
        )

        self.paginas.addWidget(
            self.pagina_ventas
        )

        self.paginas.addWidget(
            self.pagina_inventario
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

        layout_principal.addWidget(
            menu
        )

        layout_principal.addWidget(
            self.paginas,
            1
        )


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

        boton.setMinimumHeight(
            45
        )

        boton.setStyleSheet(
            ESTILO_BOTON_MENU
        )

        self.botones_menu.append(
            boton
        )

        return boton


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

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            40,
            40,
            40,
            40
        )


        lbl_titulo = QLabel(
            titulo
        )

        lbl_titulo.setStyleSheet(
            ESTILO_TITULO_PAGINA
        )


        lbl_descripcion = QLabel(
            descripcion
        )

        lbl_descripcion.setStyleSheet(
            ESTILO_DESCRIPCION_PAGINA
        )


        layout.addWidget(
            lbl_titulo
        )

        layout.addSpacing(
            10
        )

        layout.addWidget(
            lbl_descripcion
        )

        layout.addStretch()


        return pagina


    # =========================================================
    # INICIO
    # =========================================================

    def abrir_inicio(self):

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
            self.pagina_buscar
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
            self.pagina_medicamentos
        )

        self.marcar_boton_activo(
            self.btn_medicamentos
        )


    # =========================================================
    # VENTAS
    # =========================================================

    def abrir_ventas(self):

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
            self.pagina_inventario
        )

        self.marcar_boton_activo(
            self.btn_inventario
        )


    # =========================================================
    # EMPLEADOS
    # =========================================================

    def abrir_empleados(self):

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