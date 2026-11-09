# inventario.py

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMessageBox,
    QTableWidgetItem,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QFrame
)

from PyQt6.QtCore import Qt

from conexion import conectar
from ui_comun import tabla, encabezado, tarjeta
from estilos import ESTILO_GENERAL, ESTILO_TEXTO_SECUNDARIO, ESTILO_VALOR, ESTILO_BOTON_SECUNDARIO


class Inventario(QWidget):

    def __init__(self, usuario):
        super().__init__()

        self.usuario = usuario

        self.id_medicamento_seleccionado = None
        self.cantidad_actual = 0

        self.crear_interfaz()
        self.cargar_inventario()


    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        self.setObjectName("superficie")
        self.setStyleSheet(ESTILO_GENERAL)
        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            24, 22, 24, 20
        )

        layout_principal.setSpacing(
            12
        )


        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = QLabel(
            "Inventario"
        )



        descripcion = QLabel(
            "Control de existencias, entradas, ajustes y devoluciones."
        )



        # =====================================================
        # USUARIO ACTUAL
        # =====================================================

        lbl_usuario = QLabel(
            f"Usuario: {self.usuario['nombre']}"
        )

        lbl_usuario.setStyleSheet(ESTILO_TEXTO_SECUNDARIO)


        # =====================================================
        # BUSCADOR
        # =====================================================

        layout_busqueda = QHBoxLayout()


        self.txt_buscar = QLineEdit()

        self.txt_buscar.setPlaceholderText(
            "Buscar por nombre, código de barras, "
            "principio activo o fabricante..."
        )

        self.txt_buscar.textChanged.connect(
            self.buscar_inventario
        )


        self.btn_actualizar = QPushButton(
            "Actualizar"
        )

        self.btn_actualizar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_actualizar.clicked.connect(
            self.cargar_inventario
        )


        layout_busqueda.addWidget(
            self.txt_buscar
        )

        layout_busqueda.addWidget(
            self.btn_actualizar
        )


        # =====================================================
        # FORMULARIO DE MOVIMIENTO
        # =====================================================

        frame_movimiento = QFrame()

        frame_movimiento.setObjectName(
            "frameMovimiento"
        )




        layout_movimiento = QGridLayout(
            frame_movimiento
        )

        layout_movimiento.setContentsMargins(
            14, 12, 14, 12
        )

        layout_movimiento.setSpacing(
            7
        )


        # =====================================================
        # MEDICAMENTO SELECCIONADO
        # =====================================================

        self.lbl_medicamento = QLabel(
            "Ningún medicamento seleccionado"
        )

        self.lbl_medicamento.setStyleSheet(ESTILO_VALOR)


        self.lbl_existencia_actual = QLabel(
            "0"
        )

        self.lbl_existencia_actual.setStyleSheet(ESTILO_VALOR)


        # =====================================================
        # TIPO DE MOVIMIENTO
        # =====================================================

        self.cmb_tipo = QComboBox()

        self.cmb_tipo.addItem(
            "Entrada",
            "ENTRADA"
        )

        self.cmb_tipo.addItem(
            "Ajuste",
            "AJUSTE"
        )

        self.cmb_tipo.addItem(
            "Devolución",
            "DEVOLUCION"
        )

        self.cmb_tipo.currentIndexChanged.connect(
            self.cambiar_tipo_movimiento
        )


        # =====================================================
        # CANTIDAD
        # =====================================================

        self.spn_cantidad = QSpinBox()

        self.spn_cantidad.setRange(
            1,
            999999
        )

        self.spn_cantidad.setValue(
            1
        )


        # =====================================================
        # DESCRIPCIÓN
        # =====================================================

        self.txt_descripcion = QTextEdit()

        self.txt_descripcion.setPlaceholderText(
            "Motivo o descripción del movimiento..."
        )

        self.txt_descripcion.setFixedHeight(
            48
        )


        # =====================================================
        # AGREGAR CAMPOS
        # =====================================================

        rotulo = QLabel("Movimiento de inventario")
        rotulo.setObjectName("seccion")
        layout_movimiento.addWidget(rotulo, 0, 0, 1, 2)
        layout_movimiento.addWidget(lbl_usuario, 0, 2, 1, 2, Qt.AlignmentFlag.AlignRight)
        self.lbl_medicamento.setWordWrap(True)
        layout_movimiento.addWidget(QLabel("Medicamento"), 1, 0)
        layout_movimiento.addWidget(self.lbl_medicamento, 1, 1)
        layout_movimiento.addWidget(QLabel("Existencia actual"), 1, 2)
        layout_movimiento.addWidget(self.lbl_existencia_actual, 1, 3)
        layout_movimiento.addWidget(QLabel("Tipo de movimiento"), 2, 0)
        layout_movimiento.addWidget(self.cmb_tipo, 2, 1)
        layout_movimiento.addWidget(QLabel("Cantidad"), 2, 2)
        layout_movimiento.addWidget(self.spn_cantidad, 2, 3)
        layout_movimiento.addWidget(QLabel("Descripción"), 3, 0)
        layout_movimiento.addWidget(self.txt_descripcion, 3, 1, 1, 3)
        layout_movimiento.setColumnStretch(1, 2)
        layout_movimiento.setColumnStretch(3, 1)

        # =====================================================
        # BOTONES
        # =====================================================

        layout_botones = QHBoxLayout()


        self.btn_registrar = QPushButton(
            "Registrar movimiento"
        )

        self.btn_registrar.setEnabled(
            False
        )

        self.btn_registrar.clicked.connect(
            self.registrar_movimiento
        )


        self.btn_limpiar = QPushButton(
            "Limpiar"
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_seleccion
        )


        layout_botones.addWidget(
            self.btn_registrar
        )

        layout_botones.addWidget(
            self.btn_limpiar
        )


        # =====================================================
        # TABLA INVENTARIO
        # =====================================================

        self.tabla = tabla([
            "Nombre",
            "Presentación",
            "Existencia",
            "Stock mínimo",
            "Código",
            "Principio activo",
            "Fabricante",
            "Ubicación"
        ])


        self.tabla.cellClicked.connect(
            self.seleccionar_medicamento
        )


        # =====================================================
        # AGREGAR TODO
        # =====================================================

        layout_principal.addLayout(encabezado(titulo, descripcion, "Inventario"))

        self.btn_actualizar.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
        self.btn_limpiar.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
        layout_principal.addWidget(tarjeta(layout_busqueda))
        self.tabla.setMinimumHeight(140)
        layout_principal.addWidget(self.tabla, 1)
        layout_botones.addStretch()
        layout_movimiento.addLayout(layout_botones, 4, 1, 1, 3)
        layout_principal.addWidget(frame_movimiento)

    # =========================================================
    # CARGAR INVENTARIO
    # =========================================================

    def cargar_inventario(self):

        self.txt_buscar.clear()

        self.obtener_inventario(
            ""
        )


    # =========================================================
    # BUSCAR
    # =========================================================

    def buscar_inventario(self):

        texto = self.txt_buscar.text().strip()

        self.obtener_inventario(
            texto
        )


    # =========================================================
    # CONSULTAR INVENTARIO
    # =========================================================

    def obtener_inventario(
        self,
        filtro=""
    ):

        conexion = conectar()

        if conexion is None:
            return

        cursor = None

        try:

            cursor = conexion.cursor(
                dictionary=True
            )


            consulta = """
                SELECT
                    m.idMedicamento,
                    m.nombre,
                    m.presentacion,
                    m.cantidad,
                    m.stockMinimo,
                    m.codigoBarras,
                    m.principioActivo,
                    m.fabricante,
                    u.codigo AS ubicacion

                FROM medicamentos m

                LEFT JOIN ubicaciones u
                ON m.idUbicacion = u.idUbicacion

                WHERE m.activo = TRUE
            """


            parametros = []


            if filtro:

                consulta += """
                    AND (
                        m.nombre LIKE %s
                        OR m.codigoBarras LIKE %s
                        OR m.principioActivo LIKE %s
                        OR m.fabricante LIKE %s
                    )
                """

                patron = f"%{filtro}%"

                parametros = [
                    patron,
                    patron,
                    patron,
                    patron
                ]


            consulta += """
                ORDER BY m.nombre
            """


            cursor.execute(
                consulta,
                parametros
            )

            registros = cursor.fetchall()


            self.tabla.setRowCount(
                len(registros)
            )


            for fila, registro in enumerate(
                registros
            ):

                item_nombre = QTableWidgetItem(
                    registro["nombre"] or ""
                )


                # =================================================
                # ID OCULTO
                # =================================================

                item_nombre.setData(
                    Qt.ItemDataRole.UserRole,
                    registro["idMedicamento"]
                )


                # =================================================
                # CANTIDAD OCULTA
                # =================================================

                item_nombre.setData(
                    Qt.ItemDataRole.UserRole + 1,
                    registro["cantidad"]
                )


                self.tabla.setItem(
                    fila,
                    0,
                    item_nombre
                )


                valores = [
                    registro["presentacion"],
                    registro["cantidad"],
                    registro["stockMinimo"],
                    registro["codigoBarras"],
                    registro["principioActivo"],
                    registro["fabricante"],
                    registro["ubicacion"]
                ]


                for columna, valor in enumerate(
                    valores,
                    start=1
                ):

                    item = QTableWidgetItem(
                        "" if valor is None else str(valor)
                    )

                    self.tabla.setItem(
                        fila,
                        columna,
                        item
                    )


        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el inventario:\n{e}"
            )


        finally:

            if cursor is not None:
                cursor.close()

            if (
                conexion is not None
                and conexion.is_connected()
            ):
                conexion.close()


    # =========================================================
    # SELECCIONAR MEDICAMENTO
    # =========================================================

    def seleccionar_medicamento(
        self,
        fila,
        columna
    ):

        item_nombre = self.tabla.item(
            fila,
            0
        )


        if item_nombre is None:
            return


        self.id_medicamento_seleccionado = (
            item_nombre.data(
                Qt.ItemDataRole.UserRole
            )
        )


        self.cantidad_actual = (
            item_nombre.data(
                Qt.ItemDataRole.UserRole + 1
            )
        )


        if self.cantidad_actual is None:
            self.cantidad_actual = 0


        self.lbl_medicamento.setText(
            item_nombre.text()
        )


        self.lbl_existencia_actual.setText(
            str(self.cantidad_actual)
        )


        self.btn_registrar.setEnabled(
            True
        )


        # Actualizamos el máximo según el tipo de movimiento.
        self.actualizar_limites_cantidad()


    # =========================================================
    # CAMBIAR TIPO DE MOVIMIENTO
    # =========================================================

    def cambiar_tipo_movimiento(self):

        self.actualizar_limites_cantidad()


    # =========================================================
    # ACTUALIZAR LÍMITES DE CANTIDAD
    # =========================================================

    def actualizar_limites_cantidad(self):

        tipo = self.cmb_tipo.currentData()


        # =====================================================
        # AJUSTE
        # El valor representa la existencia final.
        # =====================================================

        if tipo == "AJUSTE":

            self.spn_cantidad.setRange(
                0,
                999999
            )


        # =====================================================
        # DEVOLUCIÓN
        # Se RESTA del inventario.
        # Nunca puede ser mayor a la existencia.
        # =====================================================

        elif tipo == "DEVOLUCION":

            if self.id_medicamento_seleccionado is None:

                self.spn_cantidad.setRange(
                    1,
                    999999
                )

            elif self.cantidad_actual > 0:

                self.spn_cantidad.setRange(
                    1,
                    self.cantidad_actual
                )

            else:

                self.spn_cantidad.setRange(
                    0,
                    0
                )


        # =====================================================
        # ENTRADA
        # =====================================================

        else:

            self.spn_cantidad.setRange(
                1,
                999999
            )


        # Evitar que quede un valor fuera del nuevo rango.
        if (
            self.spn_cantidad.value()
            > self.spn_cantidad.maximum()
        ):

            self.spn_cantidad.setValue(
                self.spn_cantidad.maximum()
            )


    # =========================================================
    # REGISTRAR MOVIMIENTO
    # =========================================================

    def registrar_movimiento(self):
        from servicios import movimiento_manual
        if self.id_medicamento_seleccionado is None:
            QMessageBox.warning(self, "Seleccione un medicamento", "Seleccione un medicamento de la tabla.")
            return
        if QMessageBox.question(self, "Confirmar movimiento", "¿Registrar este movimiento de inventario?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            nueva = movimiento_manual(self.usuario, self.id_medicamento_seleccionado,
                self.cmb_tipo.currentData(), self.spn_cantidad.value(),
                self.txt_descripcion.toPlainText().strip(), self.cantidad_actual)
        except ValueError as exc:
            QMessageBox.warning(self, "No se pudo registrar", str(exc))
            return
        QMessageBox.information(self, "Movimiento registrado", f"Nueva existencia: {nueva}.")
        self.limpiar_seleccion()
        self.cargar_inventario()


    def limpiar_seleccion(self):

        self.id_medicamento_seleccionado = None

        self.cantidad_actual = 0


        self.lbl_medicamento.setText(
            "Ningún medicamento seleccionado"
        )

        self.lbl_existencia_actual.setText(
            "0"
        )


        self.cmb_tipo.setCurrentIndex(
            0
        )


        self.spn_cantidad.setRange(
            1,
            999999
        )

        self.spn_cantidad.setValue(
            1
        )


        self.txt_descripcion.clear()


        self.btn_registrar.setEnabled(
            False
        )


        self.tabla.clearSelection()
