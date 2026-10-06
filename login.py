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

from estilos import (
    ESTILO_GENERAL,
    ESTILO_TITULO,
    ESTILO_SUBTITULO,
    ESTILO_LABEL,
    ESTILO_FRAME_LOGIN,
    ESTILO_TEXTO_SECUNDARIO
)


class Login(QWidget):

    def __init__(self):
        super().__init__()

        self.ventana_principal = None

        self.setWindowTitle(
            "Sistema de Farmacia - Login"
        )

        self.setFixedSize(
            440,
            480
        )

        self.crear_interfaz()


    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        self.setStyleSheet(
            ESTILO_GENERAL
        )

        # -----------------------------------------------------
        # LAYOUT PRINCIPAL
        # -----------------------------------------------------

        layout_principal = QVBoxLayout()

        layout_principal.setContentsMargins(
            40,
            35,
            40,
            35
        )

        layout_principal.setSpacing(
            15
        )


        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = QLabel(
            "SISTEMA DE FARMACIA"
        )

        titulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        titulo.setStyleSheet(
            ESTILO_TITULO
        )


        # =====================================================
        # SUBTÍTULO
        # =====================================================

        subtitulo = QLabel(
            "Inicio de sesión"
        )

        subtitulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        subtitulo.setStyleSheet(
            ESTILO_SUBTITULO
        )


        # =====================================================
        # DESCRIPCIÓN
        # =====================================================

        descripcion = QLabel(
            "Ingrese sus credenciales para acceder al sistema"
        )

        descripcion.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        descripcion.setWordWrap(
            True
        )

        descripcion.setStyleSheet(
            ESTILO_TEXTO_SECUNDARIO
        )


        # =====================================================
        # FRAME
        # =====================================================

        frame = QFrame()

        frame.setObjectName(
            "frameLogin"
        )

        frame.setStyleSheet(
            ESTILO_FRAME_LOGIN
        )

        layout_formulario = QVBoxLayout(
            frame
        )

        layout_formulario.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout_formulario.setSpacing(
            12
        )


        # =====================================================
        # USUARIO
        # =====================================================

        lbl_usuario = QLabel(
            "Usuario"
        )

        lbl_usuario.setStyleSheet(
            ESTILO_LABEL
        )

        self.txt_usuario = QLineEdit()

        self.txt_usuario.setPlaceholderText(
            "Ingrese su usuario"
        )

        self.txt_usuario.setClearButtonEnabled(
            True
        )


        # =====================================================
        # CONTRASEÑA
        # =====================================================

        lbl_contrasena = QLabel(
            "Contraseña"
        )

        lbl_contrasena.setStyleSheet(
            ESTILO_LABEL
        )

        self.txt_contrasena = QLineEdit()

        self.txt_contrasena.setPlaceholderText(
            "Ingrese su contraseña"
        )

        self.txt_contrasena.setEchoMode(
            QLineEdit.EchoMode.Password
        )


        # =====================================================
        # BOTÓN
        # =====================================================

        self.btn_ingresar = QPushButton(
            "INICIAR SESIÓN"
        )

        self.btn_ingresar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_ingresar.clicked.connect(
            self.iniciar_sesion
        )

        self.txt_contrasena.returnPressed.connect(
            self.iniciar_sesion
        )


        # =====================================================
        # AGREGAR AL FORMULARIO
        # =====================================================

        layout_formulario.addWidget(
            lbl_usuario
        )

        layout_formulario.addWidget(
            self.txt_usuario
        )

        layout_formulario.addSpacing(
            5
        )

        layout_formulario.addWidget(
            lbl_contrasena
        )

        layout_formulario.addWidget(
            self.txt_contrasena
        )

        layout_formulario.addSpacing(
            15
        )

        layout_formulario.addWidget(
            self.btn_ingresar
        )


        # =====================================================
        # AGREGAR AL LAYOUT PRINCIPAL
        # =====================================================

        layout_principal.addWidget(
            titulo
        )

        layout_principal.addWidget(
            subtitulo
        )

        layout_principal.addWidget(
            descripcion
        )

        layout_principal.addSpacing(
            10
        )

        layout_principal.addWidget(
            frame
        )

        layout_principal.addStretch()


        self.setLayout(
            layout_principal
        )

        self.txt_usuario.setFocus()


    # =========================================================
    # INICIAR SESIÓN
    # =========================================================

    def iniciar_sesion(self):

        usuario = self.txt_usuario.text().strip()

        contrasena = self.txt_contrasena.text().strip()


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
            # POR AHORA SIN BCRYPT
            # =================================================

            if contrasena != resultado["contrasena"]:

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

            self.ventana_principal.show()

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

    ventana = Login()

    ventana.show()

    sys.exit(
        app.exec()
    )