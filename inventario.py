# inventario.py

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QFrame
)

from PyQt6.QtCore import Qt

from conexion import conectar


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

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            30, 25, 30, 25
        )

        layout_principal.setSpacing(
            15
        )


        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = QLabel(
            "Inventario"
        )

        titulo.setStyleSheet("""
            QLabel {
                color: #1565C0;
                font-size: 28px;
                font-weight: bold;
                background-color: transparent;
            }
        """)


        descripcion = QLabel(
            "Control de existencias, entradas, ajustes y devoluciones."
        )

        descripcion.setStyleSheet("""
            QLabel {
                color: #607D8B;
                font-size: 14px;
                background-color: transparent;
            }
        """)


        # =====================================================
        # USUARIO ACTUAL
        # =====================================================

        lbl_usuario = QLabel(
            f"Usuario: {self.usuario['nombre']}"
        )

        lbl_usuario.setStyleSheet("""
            QLabel {
                color: #546E7A;
                font-size: 13px;
                background-color: transparent;
            }
        """)


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

        frame_movimiento.setStyleSheet("""
            QFrame#frameMovimiento {
                background-color: #FFFFFF;
                border: 1px solid #D6E4F0;
                border-radius: 10px;
            }

            QLabel {
                background-color: transparent;
                border: none;
                color: #37474F;
                font-weight: bold;
            }
        """)


        layout_movimiento = QFormLayout(
            frame_movimiento
        )

        layout_movimiento.setContentsMargins(
            20, 20, 20, 20
        )

        layout_movimiento.setSpacing(
            12
        )


        # =====================================================
        # MEDICAMENTO SELECCIONADO
        # =====================================================

        self.lbl_medicamento = QLabel(
            "Ningún medicamento seleccionado"
        )

        self.lbl_medicamento.setStyleSheet("""
            QLabel {
                color: #1565C0;
                font-size: 15px;
                font-weight: bold;
                background-color: transparent;
            }
        """)


        self.lbl_existencia_actual = QLabel(
            "0"
        )

        self.lbl_existencia_actual.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 16px;
                font-weight: bold;
                background-color: transparent;
            }
        """)


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
            70
        )


        # =====================================================
        # AGREGAR CAMPOS
        # =====================================================

        layout_movimiento.addRow(
            "Medicamento:",
            self.lbl_medicamento
        )

        layout_movimiento.addRow(
            "Existencia actual:",
            self.lbl_existencia_actual
        )

        layout_movimiento.addRow(
            "Tipo de movimiento:",
            self.cmb_tipo
        )

        layout_movimiento.addRow(
            "Cantidad:",
            self.spn_cantidad
        )

        layout_movimiento.addRow(
            "Descripción:",
            self.txt_descripcion
        )


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

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(
            8
        )

        self.tabla.setHorizontalHeaderLabels([
            "Nombre",
            "Presentación",
            "Existencia",
            "Stock mínimo",
            "Código",
            "Principio activo",
            "Fabricante",
            "Ubicación"
        ])


        self.tabla.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabla.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabla.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabla.verticalHeader().setVisible(
            False
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla.cellClicked.connect(
            self.seleccionar_medicamento
        )


        # =====================================================
        # AGREGAR TODO
        # =====================================================

        layout_principal.addWidget(
            titulo
        )

        layout_principal.addWidget(
            descripcion
        )

        layout_principal.addWidget(
            lbl_usuario
        )

        layout_principal.addLayout(
            layout_busqueda
        )

        layout_principal.addWidget(
            frame_movimiento
        )

        layout_principal.addLayout(
            layout_botones
        )

        layout_principal.addWidget(
            self.tabla
        )


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

        if self.id_medicamento_seleccionado is None:

            QMessageBox.warning(
                self,
                "Seleccione un medicamento",
                "Seleccione un medicamento de la tabla."
            )

            return


        tipo = self.cmb_tipo.currentData()

        cantidad = self.spn_cantidad.value()

        descripcion = (
            self.txt_descripcion
            .toPlainText()
            .strip()
        )


        # =====================================================
        # ENTRADA
        # SUMA EXISTENCIA
        # =====================================================

        if tipo == "ENTRADA":

            cantidad_nueva = (
                self.cantidad_actual
                + cantidad
            )


        # =====================================================
        # DEVOLUCIÓN
        # RESTA EXISTENCIA
        # =====================================================

        elif tipo == "DEVOLUCION":

            if self.cantidad_actual <= 0:

                QMessageBox.warning(
                    self,
                    "Sin existencia",
                    "Este medicamento no tiene existencias para devolver."
                )

                return


            if cantidad > self.cantidad_actual:

                QMessageBox.warning(
                    self,
                    "Cantidad inválida",
                    (
                        "No puede devolver más unidades "
                        "de las disponibles.\n\n"
                        f"Existencia actual: {self.cantidad_actual}"
                    )
                )

                return


            cantidad_nueva = (
                self.cantidad_actual
                - cantidad
            )


        # =====================================================
        # AJUSTE
        # EL NÚMERO ES LA NUEVA EXISTENCIA TOTAL
        # =====================================================

        elif tipo == "AJUSTE":

            cantidad_nueva = cantidad


        else:

            QMessageBox.warning(
                self,
                "Movimiento inválido",
                "Seleccione un tipo de movimiento válido."
            )

            return


        # =====================================================
        # EVITAR EXISTENCIA NEGATIVA
        # =====================================================

        if cantidad_nueva < 0:

            QMessageBox.warning(
                self,
                "Existencia inválida",
                "La existencia no puede quedar en números negativos."
            )

            return


        # =====================================================
        # AJUSTE SIN CAMBIOS
        # =====================================================

        if (
            tipo == "AJUSTE"
            and cantidad_nueva == self.cantidad_actual
        ):

            QMessageBox.information(
                self,
                "Sin cambios",
                "La cantidad indicada es igual a la existencia actual."
            )

            return


        # =====================================================
        # DESCRIPCIÓN OBLIGATORIA PARA AJUSTE
        # =====================================================

        if (
            tipo == "AJUSTE"
            and not descripcion
        ):

            QMessageBox.warning(
                self,
                "Descripción requerida",
                "Indique el motivo del ajuste de inventario."
            )

            self.txt_descripcion.setFocus()

            return


        # =====================================================
        # DESCRIPCIÓN OBLIGATORIA PARA DEVOLUCIÓN
        # =====================================================

        if (
            tipo == "DEVOLUCION"
            and not descripcion
        ):

            QMessageBox.warning(
                self,
                "Descripción requerida",
                (
                    "Indique el motivo de la devolución.\n\n"
                    "Ejemplo: Producto caducado."
                )
            )

            self.txt_descripcion.setFocus()

            return


        # =====================================================
        # CONFIRMACIÓN
        # =====================================================

        mensaje = (
            f"Medicamento: {self.lbl_medicamento.text()}\n\n"
            f"Existencia actual: {self.cantidad_actual}\n"
            f"Nueva existencia: {cantidad_nueva}\n\n"
            f"¿Desea registrar el movimiento?"
        )


        respuesta = QMessageBox.question(
            self,
            "Confirmar movimiento",
            mensaje,
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )


        if (
            respuesta
            != QMessageBox.StandardButton.Yes
        ):

            return


        # =====================================================
        # CONEXIÓN
        # =====================================================

        conexion = conectar()

        if conexion is None:
            return

        cursor = None


        try:

            cursor = conexion.cursor()


            # =================================================
            # ACTUALIZAR MEDICAMENTO
            # =================================================

            consulta_actualizar = """
                UPDATE medicamentos

                SET cantidad = %s

                WHERE idMedicamento = %s
                AND activo = TRUE
            """


            cursor.execute(
                consulta_actualizar,
                (
                    cantidad_nueva,
                    self.id_medicamento_seleccionado
                )
            )


            if cursor.rowcount == 0:

                conexion.rollback()

                QMessageBox.warning(
                    self,
                    "No actualizado",
                    "No se pudo actualizar el medicamento."
                )

                return


            # =================================================
            # CANTIDAD DEL MOVIMIENTO
            # =================================================

            if tipo == "AJUSTE":

                cantidad_movimiento = abs(
                    cantidad_nueva
                    - self.cantidad_actual
                )

            else:

                cantidad_movimiento = cantidad


            # =================================================
            # REGISTRAR MOVIMIENTO
            # =================================================

            consulta_movimiento = """
                INSERT INTO movimientos_inventario
                (
                    idMedicamento,
                    idUsuario,
                    idVenta,
                    tipo,
                    cantidad,
                    cantidadAnterior,
                    cantidadNueva,
                    descripcion
                )

                VALUES
                (
                    %s,
                    %s,
                    NULL,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """


            cursor.execute(
                consulta_movimiento,
                (
                    self.id_medicamento_seleccionado,
                    self.usuario["idUsuario"],
                    tipo,
                    cantidad_movimiento,
                    self.cantidad_actual,
                    cantidad_nueva,
                    descripcion if descripcion else None
                )
            )


            # =================================================
            # CONFIRMAR TODO
            # =================================================

            conexion.commit()


            QMessageBox.information(
                self,
                "Movimiento registrado",
                (
                    "El movimiento se registró correctamente.\n\n"
                    f"Existencia anterior: {self.cantidad_actual}\n"
                    f"Existencia nueva: {cantidad_nueva}"
                )
            )


            self.limpiar_seleccion()

            self.cargar_inventario()


        except Exception as e:

            conexion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo registrar el movimiento:\n{e}"
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
    # LIMPIAR
    # =========================================================

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