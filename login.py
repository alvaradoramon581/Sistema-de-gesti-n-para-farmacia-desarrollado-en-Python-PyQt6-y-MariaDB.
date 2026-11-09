import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QFrame
)

from PyQt6.QtCore import Qt

from conexion import conectar
from seguridad import verificar_contrasena
from ui_comun import configurar_pantalla_completa, logo_farmacia

from estilos import (
    ESTILO_GENERAL,
    ESTILO_TITULO_PAGINA,
    ESTILO_LABEL,
    ESTILO_TEXTO_SECUNDARIO
)


class Login(QWidget):

    def __init__(self):
        super().__init__()

        self.ventana_principal = None

        self.setWindowTitle(
            "Sistema de Farmacia - Login"
        )

        self.resize(
            440,
            480
        )

        self.crear_interfaz()
        configurar_pantalla_completa(self)


    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        self.setObjectName("superficie")
        self.setStyleSheet(ESTILO_GENERAL)
        exterior = QVBoxLayout(self)
        exterior.setContentsMargins(18, 18, 18, 18)
        panel = QFrame()
        panel.setObjectName("frameLogin")
        panel.setMaximumWidth(440)
        layout_principal = QVBoxLayout(panel)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        layout_principal.addSpacing(12)
        layout_principal.addWidget(logo_farmacia(182, 148), alignment=Qt.AlignmentFlag.AlignHCenter)

        frame = QFrame()
        layout_formulario = QVBoxLayout(frame)
        layout_formulario.setContentsMargins(22, 8, 22, 20)
        layout_formulario.setSpacing(6)

        layout_formulario.addSpacing(5)
        lbl_usuario = QLabel("Usuario")
        lbl_usuario.setStyleSheet(ESTILO_LABEL)
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Ingrese su usuario")
        self.txt_usuario.setClearButtonEnabled(True)
        layout_formulario.addWidget(lbl_usuario)
        layout_formulario.addWidget(self.txt_usuario)
        layout_formulario.addSpacing(5)
        lbl_contrasena = QLabel("Contraseña")
        lbl_contrasena.setStyleSheet(ESTILO_LABEL)
        self.txt_contrasena = QLineEdit()
        self.txt_contrasena.setPlaceholderText("Ingrese su contraseña")
        self.txt_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        layout_formulario.addWidget(lbl_contrasena)
        layout_formulario.addWidget(self.txt_contrasena)
        layout_formulario.addSpacing(10)
        self.btn_ingresar = QPushButton("INICIAR SESIÓN")
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ingresar.clicked.connect(self.iniciar_sesion)
        self.txt_contrasena.returnPressed.connect(self.iniciar_sesion)
        layout_formulario.addWidget(self.btn_ingresar)
        layout_principal.addWidget(frame)
        exterior.addStretch()
        exterior.addWidget(panel)
        exterior.setAlignment(panel, Qt.AlignmentFlag.AlignHCenter)
        exterior.addStretch()
        panel.setMinimumWidth(335)
        self.txt_usuario.setFocus()


    # =========================================================
    # INICIAR SESIÓN
    # =========================================================

    def iniciar_sesion(self):

        usuario = self.txt_usuario.text().strip()

        contrasena = self.txt_contrasena.text()


        # =====================================================
        # VALIDAR CAMPOS
        # =====================================================

        if not usuario or not contrasena:

            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Ingrese usuario y contraseña."
            )

            return


        # =====================================================
        # CONEXIÓN
        # =====================================================

        conexion = conectar()

        if conexion is None:

            QMessageBox.critical(
                self,
                "Error de conexión",
                "No se pudo conectar con la base de datos."
            )

            return


        cursor = None


        try:

            cursor = conexion.cursor(
                dictionary=True
            )


            # =================================================
            # CONSULTA
            # =================================================

            consulta = """
                SELECT
                    idUsuario,
                    nombre,
                    usuario,
                    contrasena,
                    rol,
                    activo
                FROM usuarios
                WHERE usuario = %s
                LIMIT 1
            """


            cursor.execute(
                consulta,
                (usuario,)
            )


            resultado = cursor.fetchone()


            # =================================================
            # USUARIO NO ENCONTRADO
            # =================================================

            if resultado is None:

                QMessageBox.warning(
                    self,
                    "Acceso denegado",
                    "Usuario o contraseña incorrectos."
                )

                self.txt_contrasena.clear()

                self.txt_contrasena.setFocus()

                return


            # =================================================
            # USUARIO INACTIVO
            # =================================================

            if not resultado["activo"]:

                QMessageBox.warning(
                    self,
                    "Usuario inactivo",
                    "Este usuario se encuentra desactivado."
                )

                return


            # =================================================
            # CONTRASEÑA
            #
            # BCRYPT Y COMPATIBILIDAD CON LAS CUENTAS EXISTENTES
            # =================================================

            if not verificar_contrasena(contrasena, resultado["contrasena"]):

                QMessageBox.warning(
                    self,
                    "Acceso denegado",
                    "Usuario o contraseña incorrectos."
                )

                self.txt_contrasena.clear()

                self.txt_contrasena.setFocus()

                return


            # =================================================
            # LOGIN CORRECTO
            # =================================================

            print(
                "=============================="
            )

            print(
                "SESIÓN INICIADA"
            )

            print(
                "ID:",
                resultado["idUsuario"]
            )

            print(
                "Nombre:",
                resultado["nombre"]
            )

            print(
                "Usuario:",
                resultado["usuario"]
            )

            print(
                "Rol:",
                resultado["rol"]
            )

            print(
                "=============================="
            )


            # =================================================
            # ABRIR VENTANA PRINCIPAL
            # =================================================

            from principal import Principal

            self.ventana_principal = Principal(
                resultado
            )

            self.ventana_principal.showFullScreen()

            self.close()


        # =====================================================
        # ERROR
        # =====================================================

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Ocurrió un error al iniciar sesión:\n\n{e}"
            )


        # =====================================================
        # CERRAR CONEXIÓN
        # =====================================================

        finally:

            if cursor is not None:

                cursor.close()


            if (
                conexion is not None
                and conexion.is_connected()
            ):

                conexion.close()


# =============================================================
# EJECUTAR
# =============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    app.setStyleSheet(ESTILO_GENERAL)
    ventana = Login()

    ventana.show()

    sys.exit(
        app.exec()
    )
