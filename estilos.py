# ============================================================
# ESTILOS GENERALES DEL SISTEMA DE FARMACIA
# ============================================================


# ============================================================
# ESTILO GENERAL
# ============================================================

ESTILO_GENERAL = """
QWidget {
    background-color: #F4F8FC;
    font-family: Arial;
    color: #263238;
}

QLabel {
    background-color: transparent;
    color: #263238;
}

QLineEdit {
    background-color: #FFFFFF;
    color: #263238;

    border: 1px solid #B0BEC5;
    border-radius: 7px;

    padding: 10px;

    font-size: 14px;
}

QLineEdit:focus {
    border: 2px solid #1976D2;
}

QComboBox {
    background-color: #FFFFFF;
    color: #263238;

    border: 1px solid #B0BEC5;
    border-radius: 7px;

    padding: 8px;

    font-size: 14px;
}

QComboBox:focus {
    border: 2px solid #1976D2;
}

QSpinBox,
QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #263238;

    border: 1px solid #B0BEC5;
    border-radius: 7px;

    padding: 8px;

    font-size: 14px;
}

QTextEdit {
    background-color: #FFFFFF;
    color: #263238;

    border: 1px solid #B0BEC5;
    border-radius: 7px;

    padding: 8px;

    font-size: 14px;
}

QPushButton {
    background-color: #1976D2;
    color: #FFFFFF;

    border: none;
    border-radius: 7px;

    padding: 10px 14px;

    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565C0;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #CFD8DC;
    color: #78909C;
}
"""


# ============================================================
# LOGIN
# ============================================================

ESTILO_TITULO = """
QLabel {
    background-color: transparent;
    color: #1565C0;

    font-size: 25px;
    font-weight: bold;
}
"""


ESTILO_SUBTITULO = """
QLabel {
    background-color: transparent;
    color: #546E7A;

    font-size: 16px;
}
"""


ESTILO_LABEL = """
QLabel {
    background-color: transparent;
    color: #37474F;

    border: none;

    font-size: 14px;
    font-weight: bold;
}
"""


ESTILO_FRAME_LOGIN = """
QFrame#frameLogin {
    background-color: #FFFFFF;

    border: 1px solid #D6E4F0;
    border-radius: 14px;
}
"""


ESTILO_TEXTO_SECUNDARIO = """
QLabel {
    background-color: transparent;

    color: #78909C;

    border: none;

    font-size: 12px;
}
"""


# ============================================================
# MENÚ LATERAL
# ============================================================

ESTILO_MENU_LATERAL = """
QFrame#menuLateral {
    background-color: #0D47A1;
    border: none;
}
"""


ESTILO_TITULO_MENU = """
QLabel {
    color: #FFFFFF;
    background-color: transparent;

    font-size: 22px;
    font-weight: bold;

    padding: 8px;
}
"""


ESTILO_NOMBRE_USUARIO_MENU = """
QLabel {
    color: #FFFFFF;
    background-color: transparent;

    font-size: 14px;
    font-weight: bold;
}
"""


ESTILO_ROL_USUARIO_MENU = """
QLabel {
    color: #BBDEFB;
    background-color: transparent;

    font-size: 12px;
}
"""


# ============================================================
# BOTÓN NORMAL DEL MENÚ
# ============================================================

ESTILO_BOTON_MENU = """
QPushButton {
    background-color: transparent;

    color: #E3F2FD;

    border: none;
    border-radius: 7px;

    padding: 12px 14px;

    text-align: left;

    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565C0;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #1976D2;
}

QPushButton:disabled {
    background-color: transparent;
    color: #78909C;
}
"""


# ============================================================
# BOTÓN ACTIVO DEL MENÚ
# ============================================================

ESTILO_BOTON_MENU_ACTIVO = """
QPushButton {
    background-color: #1976D2;

    color: #FFFFFF;

    border: none;
    border-left: 5px solid #90CAF9;
    border-radius: 7px;

    padding: 12px 14px;

    text-align: left;

    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1976D2;
}
"""


# ============================================================
# BOTÓN CERRAR SESIÓN
# ============================================================

ESTILO_BOTON_CERRAR = """
QPushButton {
    background-color: transparent;

    color: #FFCDD2;

    border: none;
    border-radius: 7px;

    padding: 12px 14px;

    text-align: left;

    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #B71C1C;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #7F0000;
}
"""


# ============================================================
# PÁGINAS GENERALES
# ============================================================

ESTILO_CONTENEDOR_PAGINAS = """
QStackedWidget {
    background-color: #F4F8FC;
}
"""


ESTILO_TITULO_PAGINA = """
QLabel {
    color: #1565C0;
    background-color: transparent;

    font-size: 28px;
    font-weight: bold;
}
"""


ESTILO_DESCRIPCION_PAGINA = """
QLabel {
    color: #546E7A;
    background-color: transparent;

    font-size: 16px;
}
"""


# ============================================================
# FRAMES / TARJETAS
# ============================================================

ESTILO_FRAME_BLANCO = """
QFrame {
    background-color: #FFFFFF;

    border: 1px solid #D6E4F0;
    border-radius: 10px;
}
"""


# ============================================================
# TABLAS
# ============================================================

ESTILO_TABLA = """
QTableWidget {
    background-color: #FFFFFF;

    color: #263238;

    border: 1px solid #D6E4F0;
    border-radius: 7px;

    gridline-color: #E0E0E0;

    selection-background-color: #BBDEFB;
    selection-color: #0D47A1;
}

QHeaderView::section {
    background-color: #E3F2FD;

    color: #1565C0;

    padding: 8px;

    border: none;
    border-bottom: 1px solid #90CAF9;

    font-size: 13px;
    font-weight: bold;
}
"""


# ============================================================
# BOTÓN SECUNDARIO
# ============================================================

ESTILO_BOTON_SECUNDARIO = """
QPushButton {
    background-color: #FFFFFF;
    color: #1976D2;

    border: 1px solid #1976D2;
    border-radius: 7px;

    padding: 10px;

    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #E3F2FD;
}

QPushButton:pressed {
    background-color: #BBDEFB;
}
"""


# ============================================================
# BOTÓN DE PELIGRO
# ============================================================

ESTILO_BOTON_PELIGRO = """
QPushButton {
    background-color: #D32F2F;
    color: #FFFFFF;

    border: none;
    border-radius: 7px;

    padding: 10px;

    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #C62828;
}

QPushButton:pressed {
    background-color: #B71C1C;
}
"""