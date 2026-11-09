"""Tema del escritorio de farmacia: superficie clara, tinta azul y navegación oscura."""
from pathlib import Path

FONDO_LOGO_PORTADA = '#DCECFB'

ESTILO_GENERAL = """
QWidget { color: #0B2E56; font-family: "Segoe UI", Arial, sans-serif; font-size: 13px; }
QMainWindow, QDialog, QStackedWidget, QWidget#superficie, QScrollArea { background: #EFF5FD; }
QScrollArea { border: none; }
QLabel, QCheckBox { background: transparent; }
QLineEdit, QComboBox, QAbstractSpinBox, QTextEdit, QPlainTextEdit {
    background: #FFFFFF; color: #0B2E56; border: 1px solid #A9BFD9;
    border-radius: 6px; padding: 6px 8px; selection-background-color: #1479D8;
}
QLineEdit, QComboBox, QAbstractSpinBox { min-height: 18px; }
QLineEdit:focus, QComboBox:focus, QAbstractSpinBox:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #1479D8; background: #FAFCFF;
}
QLineEdit:disabled, QComboBox:disabled, QAbstractSpinBox:disabled {
    background: #EDF2F6; color: #637586; border-color: #D5DFE7;
}
QComboBox QAbstractItemView { background: white; selection-background-color: #DCEBFA; selection-color: #103D70; }
QComboBox, QAbstractSpinBox { padding-right: 22px; }
QComboBox::drop-down, QDateEdit::drop-down {
    subcontrol-origin: border; subcontrol-position: center right; width: 21px; border: none;
}
QSpinBox::up-button, QDoubleSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border; width: 19px; height: 14px; border: none; background: transparent;
}
QSpinBox::up-button, QDoubleSpinBox::up-button { subcontrol-position: top right; margin-top: 2px; }
QSpinBox::down-button, QDoubleSpinBox::down-button { subcontrol-position: bottom right; margin-bottom: 2px; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: url("@recursos/flecha-arriba.svg"); width: 9px; height: 6px; }
QComboBox::down-arrow, QDateEdit::down-arrow, QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url("@recursos/flecha-abajo.svg"); width: 9px; height: 6px;
}
QPushButton { background: #0064C9; color: white; border: 1px solid #0064C9;
    padding: 7px 13px; border-radius: 6px; font-weight: 600; }
QPushButton:hover { background: #045AB2; border-color: #045AB2; }
QPushButton:pressed { background: #08468F; border-color: #08468F; }
QPushButton:focus { border: 1px solid #15344D; }
QPushButton:disabled { background: #E8EEF3; border-color: #D5DFE7; color: #657786; }
QFrame#tarjeta, QFrame#frameMovimiento, QFrame#frameMedicamentos, QFrame#panelInformacion,
QFrame#panelMapa, QFrame#frameLogin { background: #FFFFFF; border: 1px solid #D6E4F5; border-radius: 10px; }
QLabel#seccion { font-size: 16px; font-weight: 700; color: #082D59; }
QLabel#logoFarmacia { background: white; border-radius: 8px; }
QLabel#insignia { background: #DCEBFF; border: 1px solid #CCE1F9; border-radius: 10px; }
QLabel#tituloPortada { color: white; font-weight: 700; }
QLabel#bienvenida { color: #FFFFFF; font-weight: 600; }
QLabel#marcaPortada { background: @placa; border-radius: 20px; }
QFrame#filetePortada { border: none; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #30A2F3,stop:1 rgba(48,162,243,0)); }
QLabel#lemaMenu { color: #7CCFFF; font-size: 9px; font-style: italic; }
QFrame#panelAlertasInicio { background: #FCFDFF; border: 1px solid #D3E1F3; border-radius: 16px; }
QLabel#tituloAlertasInicio { color: #082C56; font-size: 21px; font-weight: 700; }
QPushButton#consultarAlertas { padding: 9px 15px; font-size: 15px; }
QLabel#conteoInicio { color: #294F7F; font-size: 15px; }
QFrame#indicador { background: #EFF5FE; border: 1px solid #D3E4FC; border-radius: 10px; }
QLabel#iconoIndicador { background: #D7E9FE; border-radius: 26px; }
QLabel#nombreIndicador { color: #0B305A; font-size: 17px; }
QLabel#valorIndicador { color: #045EBE; font-size: 34px; font-weight: 700; }
QLabel#resumen { background: #EAF2FD; border-radius: 5px; padding: 6px 10px; color: #204A79; }
QToolTip { color: #FFFFFF; background: #092E55; border: none; padding: 4px; }
QMessageBox QLabel { padding: 4px; }
QGraphicsView { background: #F3F8FF; border: 1px solid #CEDFF3; border-radius: 6px; }
QScrollBar:vertical { background: #EEF4FC; width: 10px; margin: 0; }
QScrollBar:horizontal { background: #EEF4FC; height: 10px; margin: 0; }
QScrollBar::handle { background: #ADBED6; border-radius: 4px; min-height: 24px; min-width: 24px; }
QScrollBar::handle:hover { background: #789DC5; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
""".replace('@recursos', (Path(__file__).resolve().parent / 'recursos').as_posix()).replace('@placa', FONDO_LOGO_PORTADA)

ESTILO_TITULO_PAGINA = "QLabel { color: #092D56; font-size: 27px; font-weight: 700; }"
ESTILO_DESCRIPCION_PAGINA = "QLabel { color: #416489; font-size: 13px; }"
ESTILO_LABEL = "QLabel { color: #204568; font-size: 13px; font-weight: 600; }"
ESTILO_TEXTO_SECUNDARIO = "QLabel { color: #416489; font-size: 12px; }"
ESTILO_VALOR = "QLabel { color: #085BAA; font-size: 16px; font-weight: 700; }"
ESTILO_TOTAL = "QLabel { color: #064D97; font-size: 21px; font-weight: 700; }"
ESTILO_MENU_LATERAL = """
QFrame#menuLateral, QScrollArea#scrollMenu { background: #052B52; border: none; }
"""
ESTILO_TITULO_MENU = "QLabel { color: white; font-size: 26px; font-weight: 700; }"
ESTILO_NOMBRE_USUARIO_MENU = "QLabel { color: white; font-size: 14px; font-weight: 600; }"
ESTILO_ROL_USUARIO_MENU = "QLabel { color: #C2DAEF; font-size: 11px; }"
ESTILO_LINEA_MENU = "QFrame { background: #386084; border: none; }"
_BOTON_MENU = """
QPushButton { background: transparent; color: #E5F1FC; text-align: left; font-size: 14px;
    border: 1px solid transparent; border-radius: 6px; padding: 7px 10px; font-weight: 600; }
QPushButton:hover { background: #124673; color: white; }
QPushButton:pressed { background: #14538F; }
QPushButton:focus { border-color: #90CAF9; }
QPushButton:disabled { background: transparent; color: #94AABD; }
"""
ESTILO_BOTON_MENU = _BOTON_MENU
ESTILO_BOTON_MENU_ACTIVO = _BOTON_MENU + """
QPushButton, QPushButton:hover { background: #0463C4; color: white; }
QPushButton:pressed { background: #084B94; }
"""
ESTILO_BOTON_CERRAR = _BOTON_MENU + """
QPushButton:hover { background: #763949; } QPushButton:pressed { background: #682F3F; }
"""
ESTILO_CONTENEDOR_PAGINAS = "QStackedWidget { background: #EFF5FD; }"
ESTILO_BOTON_SECUNDARIO = """
QPushButton { background: white; color: #105B9E; border: 1px solid #B9CEE6; }
QPushButton:hover { background: #EDF5FC; border-color: #80A5C4; }
QPushButton:pressed { background: #D9EAF8; }
QPushButton:focus { border-color: #0064C9; }
QPushButton:disabled { background: #F0F4F7; color: #697B89; border-color: #D5DFE7; }
"""
ESTILO_BOTON_PELIGRO = ESTILO_BOTON_SECUNDARIO + """
QPushButton:enabled { background: #FFF8F7; color: #9F3336; border-color: #DAACAA; }
QPushButton:hover:enabled { background: #FCE8E6; } QPushButton:pressed:enabled { background: #F4D6D3; }
"""
ESTILO_TABLA = """
QTableWidget { background: white; color: #0B2E56; border: 1px solid #C8DAED;
    border-radius: 7px; selection-background-color: #D8EAFF; selection-color: #093766; }
QTableWidget::item { padding: 0 3px; border-bottom: 1px solid #E3ECF8; }
QTableWidget::item:selected { background: #D8EAFF; color: #093766; }
QHeaderView { background: #E4EEFB; }
QHeaderView::section { background: #E4EEFB; color: #10447A; border: none;
    border-bottom: 1px solid #C0D7EE; font-size: 12px; font-weight: 700; padding: 8px 4px; }
"""
ESTILO_CARITAS = """
QToolButton { background: white; color: #15365A; border: 2px solid #D6E4F5; border-radius: 8px; padding: 6px; }
QToolButton:hover, QToolButton:focus { border-color: #78ADE4; background: #F2F7FE; }
QToolButton:pressed { background: #D8EAFF; }
QToolButton:disabled { color: #667C8C; }
QToolButton:checked { background: #E2EFFF; border-color: #0064C9; color: #08468F; }
"""
