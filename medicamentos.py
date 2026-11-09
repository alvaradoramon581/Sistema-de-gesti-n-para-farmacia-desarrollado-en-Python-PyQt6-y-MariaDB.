# medicamentos.py

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QMessageBox,
    QTableWidgetItem,
    QComboBox,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QFrame,
    QDialog,
    QScrollArea,
    QDateEdit,
    QCheckBox
)

from PyQt6.QtCore import Qt, QDate

from conexion import conectar
from ui_comun import tabla, encabezado, tarjeta, dimensionar_dialogo
from estilos import ESTILO_GENERAL, ESTILO_LABEL, ESTILO_BOTON_SECUNDARIO, ESTILO_BOTON_PELIGRO


class Medicamentos(QWidget):

    def __init__(self):
        super().__init__()

        self.id_medicamento_seleccionado = None
        self.estado_medicamento_seleccionado = None

        self.crear_interfaz()
        self.cargar_ubicaciones()
        self.cargar_medicamentos()


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

        titulo = QLabel("Medicamentos")


        descripcion = QLabel(
            "Registro y administración de medicamentos y productos."
        )



        # =====================================================
        # FILTROS Y BÚSQUEDA
        # =====================================================

        layout_filtros = QHBoxLayout()

        lbl_estado = QLabel("Estado:")

        lbl_estado.setStyleSheet(ESTILO_LABEL)

        self.cmb_estado = QComboBox()

        self.cmb_estado.addItem(
            "Activos",
            "ACTIVOS"
        )

        self.cmb_estado.addItem(
            "Inactivos",
            "INACTIVOS"
        )

        self.cmb_estado.addItem(
            "Todos",
            "TODOS"
        )

        self.cmb_estado.currentIndexChanged.connect(
            self.buscar_medicamentos
        )


        self.txt_buscar = QLineEdit()

        self.txt_buscar.setPlaceholderText(
            "Buscar por nombre, código de barras, "
            "principio activo o fabricante..."
        )

        self.txt_buscar.textChanged.connect(
            self.buscar_medicamentos
        )


        self.btn_actualizar = QPushButton(
            "Actualizar"
        )

        self.btn_actualizar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_actualizar.clicked.connect(
            self.cargar_medicamentos
        )


        layout_filtros.addWidget(
            lbl_estado
        )

        layout_filtros.addWidget(
            self.cmb_estado
        )

        layout_filtros.addWidget(
            self.txt_buscar,
            1
        )

        layout_filtros.addWidget(
            self.btn_actualizar
        )


        # =====================================================
        # FORMULARIO
        # =====================================================

        frame_formulario = QFrame()

        frame_formulario.setObjectName(
            "frameMedicamentos"
        )




        layout_formulario = QFormLayout(
            frame_formulario
        )

        layout_formulario.setContentsMargins(
            20, 20, 20, 20
        )

        layout_formulario.setSpacing(9)
        layout_formulario.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)


        # =====================================================
        # CAMPOS
        # =====================================================

        self.txt_nombre = QLineEdit()

        self.txt_nombre.setPlaceholderText(
            "Ej. Paracetamol 500 mg"
        )


        self.txt_presentacion = QLineEdit()

        self.txt_presentacion.setPlaceholderText(
            "Ej. Caja con 20 tabletas"
        )


        self.spn_cantidad = QSpinBox()

        self.spn_cantidad.setRange(
            0,
            999999
        )


        self.txt_lote = QLineEdit()
        self.txt_lote.setMaxLength(60)
        self.txt_lote.setPlaceholderText("Código impreso en el envase")

        self.fecha_caducidad = QDateEdit(QDate.currentDate())
        self.fecha_caducidad.setDisplayFormat("dd/MM/yyyy")
        self.fecha_caducidad.setCalendarPopup(True)
        self.sin_caducidad = QCheckBox("Sin fecha registrada")
        self.sin_caducidad.toggled.connect(self.fecha_caducidad.setDisabled)
        self.sin_caducidad.setChecked(True)
        fila_caducidad = QHBoxLayout()
        fila_caducidad.addWidget(self.fecha_caducidad)
        fila_caducidad.addWidget(self.sin_caducidad)

        self.txt_codigo = QLineEdit()

        self.txt_codigo.setPlaceholderText(
            "Código de barras"
        )


        self.txt_principio = QLineEdit()

        self.txt_principio.setPlaceholderText(
            "Ej. Paracetamol"
        )


        self.txt_fabricante = QLineEdit()

        self.txt_fabricante.setPlaceholderText(
            "Fabricante o laboratorio"
        )


        self.txt_contenido = QLineEdit()

        self.txt_contenido.setPlaceholderText(
            "Ej. 500 mg"
        )


        self.spn_precio_compra = QDoubleSpinBox()

        self.spn_precio_compra.setRange(
            0,
            9999999
        )

        self.spn_precio_compra.setDecimals(
            2
        )

        self.spn_precio_compra.setPrefix(
            "$ "
        )


        self.spn_precio_venta = QDoubleSpinBox()

        self.spn_precio_venta.setRange(
            0,
            9999999
        )

        self.spn_precio_venta.setDecimals(
            2
        )

        self.spn_precio_venta.setPrefix(
            "$ "
        )


        self.spn_stock_minimo = QSpinBox()

        self.spn_stock_minimo.setRange(
            0,
            999999
        )

        self.spn_stock_minimo.setValue(
            5
        )


        self.cmb_ubicacion = QComboBox()

        self.cmb_ubicacion.addItem(
            "Sin ubicación",
            None
        )


        self.txt_descripcion = QTextEdit()

        self.txt_descripcion.setPlaceholderText(
            "Descripción del medicamento..."
        )

        self.txt_descripcion.setFixedHeight(
            70
        )


        # =====================================================
        # AGREGAR CAMPOS
        # =====================================================

        datos = QLabel("Datos del medicamento")
        datos.setObjectName("seccion")
        layout_formulario.addRow(datos)
        layout_formulario.addRow(
            "Nombre:",
            self.txt_nombre
        )

        layout_formulario.addRow(
            "Presentación:",
            self.txt_presentacion
        )

        layout_formulario.addRow(
            "Cantidad:",
            self.spn_cantidad
        )

        layout_formulario.addRow(
            "Código de barras:",
            self.txt_codigo
        )

        layout_formulario.addRow("Lote:", self.txt_lote)
        layout_formulario.addRow("Caducidad:", fila_caducidad)

        layout_formulario.addRow(
            "Principio activo:",
            self.txt_principio
        )

        layout_formulario.addRow(
            "Fabricante:",
            self.txt_fabricante
        )

        layout_formulario.addRow(
            "Contenido:",
            self.txt_contenido
        )

        existencias = QLabel("Precios e inventario")
        existencias.setObjectName("seccion")
        layout_formulario.addRow(existencias)
        layout_formulario.addRow(
            "Precio compra:",
            self.spn_precio_compra
        )

        layout_formulario.addRow(
            "Precio venta:",
            self.spn_precio_venta
        )

        layout_formulario.addRow(
            "Stock mínimo:",
            self.spn_stock_minimo
        )

        layout_formulario.addRow(
            "Ubicación:",
            self.cmb_ubicacion
        )

        layout_formulario.addRow(
            "Descripción:",
            self.txt_descripcion
        )


        # =====================================================
        # BOTONES
        # =====================================================

        layout_botones = QHBoxLayout()


        self.btn_guardar = QPushButton(
            "Registrar medicamento"
        )

        self.btn_modificar = QPushButton(
            "Modificar"
        )


        self.btn_desactivar = QPushButton(
            "Desactivar"
        )

        self.btn_reactivar = QPushButton(
            "Reactivar"
        )


        self.btn_modificar.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
        self.btn_desactivar.setStyleSheet(ESTILO_BOTON_PELIGRO)
        self.btn_reactivar.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
        self.btn_actualizar.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
        self.btn_guardar.clicked.connect(
            self.abrir_alta
        )

        self.btn_modificar.clicked.connect(
            self.abrir_edicion
        )


        self.btn_desactivar.clicked.connect(
            self.desactivar_medicamento
        )

        self.btn_reactivar.clicked.connect(
            self.reactivar_medicamento
        )


        layout_botones.addWidget(
            self.btn_guardar
        )

        layout_botones.addWidget(
            self.btn_modificar
        )


        layout_botones.addWidget(
            self.btn_desactivar
        )

        layout_botones.addWidget(
            self.btn_reactivar
        )


        # =====================================================
        # ESTADO INICIAL DE BOTONES
        # =====================================================

        self.btn_modificar.setEnabled(
            False
        )

        self.btn_desactivar.setEnabled(
            False
        )

        self.btn_reactivar.setEnabled(
            False
        )


        # =====================================================
        # TABLA
        # =====================================================

        self.tabla = tabla([
            "Nombre",
            "Presentación",
            "Cantidad",
            "Código",
            "Principio activo",
            "Fabricante",
            "Precio venta",
            "Stock mínimo",
            "Ubicación",
            "Estado",
            "Lote",
            "Caducidad"
        ])


        self.tabla.itemSelectionChanged.connect(self.actualizar_seleccion)
        self.tabla.cellDoubleClicked.connect(self.abrir_edicion)


        # =====================================================
        # AGREGAR TODO
        # =====================================================

        layout_principal.addLayout(encabezado(titulo, descripcion, "Medicamentos"))

        layout_principal.addWidget(tarjeta(layout_filtros))

        self.dialogo = QDialog(self)
        dimensionar_dialogo(self.dialogo, 660, 640)
        contenedor = QVBoxLayout(self.dialogo)
        desplazamiento = QScrollArea()
        desplazamiento.setWidgetResizable(True)
        desplazamiento.setWidget(frame_formulario)
        contenedor.addWidget(desplazamiento)
        acciones = QHBoxLayout()
        acciones.addStretch()
        cancelar = QPushButton("Cancelar")
        cancelar.setStyleSheet(ESTILO_BOTON_SECUNDARIO)
        cancelar.clicked.connect(self.dialogo.reject)
        self.btn_confirmar = QPushButton("Guardar")
        self.btn_confirmar.clicked.connect(self.confirmar_formulario)
        acciones.addWidget(cancelar)
        acciones.addWidget(self.btn_confirmar)
        contenedor.addLayout(acciones)

        layout_botones.addStretch()
        layout_principal.addLayout(
            layout_botones
        )

        layout_principal.addWidget(
            self.tabla
        )


    # =========================================================
    # CARGAR UBICACIONES
    # =========================================================

    def actualizar_seleccion(self):
        fila = self.tabla.currentRow()
        seleccion = self.tabla.selectedItems()
        item = self.tabla.item(fila, 0) if fila >= 0 and seleccion else None
        self.id_medicamento_seleccionado = item.data(Qt.ItemDataRole.UserRole) if item else None
        self.estado_medicamento_seleccionado = item.data(Qt.ItemDataRole.UserRole + 1) if item else None
        self.btn_modificar.setEnabled(item is not None)
        self.btn_desactivar.setEnabled(bool(item and self.estado_medicamento_seleccionado))
        self.btn_reactivar.setEnabled(bool(item and not self.estado_medicamento_seleccionado))

    def abrir_alta(self):
        self.limpiar_formulario()
        self.dialogo.setWindowTitle("Registrar medicamento")
        self.dialogo.exec()

    def abrir_edicion(self, *_):
        fila = self.tabla.currentRow()
        if fila >= 0 and self.tabla.selectedItems() and self.seleccionar_medicamento(fila, 0):
            self.dialogo.setWindowTitle("Modificar medicamento")
            self.dialogo.exec()

    def confirmar_formulario(self):
        if self.id_medicamento_seleccionado is None:
            guardado = self.guardar_medicamento()
        else:
            guardado = self.modificar_medicamento()
        if guardado:
            self.dialogo.accept()

    def cargar_ubicaciones(self):

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
                    idUbicacion,
                    codigo,
                    pasillo,
                    estante,
                    nivel
                FROM ubicaciones
                WHERE activo = TRUE
                ORDER BY codigo
            """

            cursor.execute(
                consulta
            )

            ubicaciones = cursor.fetchall()


            self.cmb_ubicacion.clear()

            self.cmb_ubicacion.addItem(
                "Sin ubicación",
                None
            )


            for ubicacion in ubicaciones:

                texto = (
                    f"{ubicacion['codigo']} - "
                    f"Pasillo {ubicacion['pasillo']} / "
                    f"Estante {ubicacion['estante']}"
                )

                if ubicacion["nivel"]:

                    texto += (
                        f" / Nivel {ubicacion['nivel']}"
                    )


                self.cmb_ubicacion.addItem(
                    texto,
                    ubicacion["idUbicacion"]
                )


        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar las ubicaciones:\n{e}"
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
    # CARGAR MEDICAMENTOS
    # =========================================================

    def cargar_medicamentos(self):

        self.txt_buscar.clear()

        self.obtener_medicamentos(
            ""
        )


    # =========================================================
    # BUSCAR
    # =========================================================

    def buscar_medicamentos(self):

        texto = self.txt_buscar.text().strip()

        self.obtener_medicamentos(
            texto
        )


    # =========================================================
    # CONSULTAR MEDICAMENTOS
    # =========================================================

    def obtener_medicamentos(
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
                    m.codigoBarras,
                    m.principioActivo,
                    m.fabricante,
                    m.precioVenta,
                    m.stockMinimo,
                    m.lote,
                    m.fechaCaducidad,
                    m.activo,

                    u.codigo AS ubicacion

                FROM medicamentos m

                LEFT JOIN ubicaciones u
                ON m.idUbicacion = u.idUbicacion

                WHERE 1 = 1
            """


            parametros = []


            # =================================================
            # FILTRO POR ESTADO
            # =================================================

            estado = self.cmb_estado.currentData()


            if estado == "ACTIVOS":

                consulta += """
                    AND m.activo = TRUE
                """


            elif estado == "INACTIVOS":

                consulta += """
                    AND m.activo = FALSE
                """


            # Si es TODOS, no se agrega condición


            # =================================================
            # FILTRO DE BÚSQUEDA
            # =================================================

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


            self.tabla.clearSelection()
            self.tabla.setRowCount(
                len(registros)
            )


            for fila, registro in enumerate(
                registros
            ):

                # =================================================
                # NOMBRE + ID OCULTO
                # =================================================

                item_nombre = QTableWidgetItem(
                    registro["nombre"] or ""
                )

                item_nombre.setData(
                    Qt.ItemDataRole.UserRole,
                    registro["idMedicamento"]
                )

                self.tabla.setItem(
                    fila,
                    0,
                    item_nombre
                )


                # =================================================
                # ESTADO OCULTO EN OTRO ROLE
                # =================================================

                item_nombre.setData(
                    Qt.ItemDataRole.UserRole + 1,
                    bool(registro["activo"])
                )


                estado_texto = (
                    "Activo"
                    if registro["activo"]
                    else "Inactivo"
                )


                valores = [
                    registro["presentacion"],
                    registro["cantidad"],
                    registro["codigoBarras"],
                    registro["principioActivo"],
                    registro["fabricante"],
                    (
                        f"${float(registro['precioVenta']):.2f}"
                        if registro["precioVenta"] is not None
                        else "$0.00"
                    ),
                    registro["stockMinimo"],
                    registro["ubicacion"],
                    estado_texto,
                    registro["lote"],
                    registro["fechaCaducidad"]
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
                f"No se pudieron cargar los medicamentos:\n{e}"
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
    # GUARDAR
    # =========================================================

    def guardar_medicamento(self):

        if not self.validar_formulario():
            return


        conexion = conectar()

        if conexion is None:
            return

        cursor = None


        try:

            cursor = conexion.cursor()


            consulta = """
                INSERT INTO medicamentos
                (
                    nombre,
                    presentacion,
                    cantidad,
                    codigoBarras,
                    descripcion,
                    principioActivo,
                    fabricante,
                    contenido,
                    precioCompra,
                    precioVenta,
                    stockMinimo,
                    idUbicacion,
                    lote,
                    fechaCaducidad,
                    activo
                )
                VALUES
                (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    TRUE
                )
            """


            datos = self.obtener_datos_formulario()


            cursor.execute(
                consulta,
                datos
            )

            conexion.commit()


            QMessageBox.information(
                self,
                "Registro guardado",
                "El medicamento se registró correctamente."
            )


            self.limpiar_formulario()

            self.cargar_medicamentos()


            return True

        except Exception as e:

            conexion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo registrar el medicamento:\n{e}"
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
    # SELECCIONAR
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


        self.estado_medicamento_seleccionado = (
            item_nombre.data(
                Qt.ItemDataRole.UserRole + 1
            )
        )


        if self.id_medicamento_seleccionado is None:
            return


        # =====================================================
        # BOTONES SEGÚN ESTADO
        # =====================================================

        self.btn_modificar.setEnabled(
            True
        )


        if self.estado_medicamento_seleccionado:

            self.btn_desactivar.setEnabled(
                True
            )

            self.btn_reactivar.setEnabled(
                False
            )

        else:

            self.btn_desactivar.setEnabled(
                False
            )

            self.btn_reactivar.setEnabled(
                True
            )


        conexion = conectar()

        if conexion is None:
            return

        cursor = None


        try:

            cursor = conexion.cursor(
                dictionary=True
            )


            consulta = """
                SELECT *
                FROM medicamentos
                WHERE idMedicamento = %s
            """


            cursor.execute(
                consulta,
                (
                    self.id_medicamento_seleccionado,
                )
            )


            medicamento = cursor.fetchone()


            if medicamento is None:
                return


            self.txt_nombre.setText(
                medicamento["nombre"] or ""
            )

            self.txt_presentacion.setText(
                medicamento["presentacion"] or ""
            )

            self.spn_cantidad.setValue(
                medicamento["cantidad"] or 0
            )
            self.spn_cantidad.setEnabled(False)
            self.spn_cantidad.setToolTip("Cambie las existencias desde Inventario.")

            self.txt_codigo.setText(
                medicamento["codigoBarras"] or ""
            )

            self.txt_lote.setText(medicamento["lote"] or "")
            fecha = medicamento["fechaCaducidad"]
            self.sin_caducidad.setChecked(fecha is None)
            self.fecha_caducidad.setDate(QDate(fecha.year, fecha.month, fecha.day) if fecha else QDate.currentDate())
            self.txt_descripcion.setPlainText(
                medicamento["descripcion"] or ""
            )

            self.txt_principio.setText(
                medicamento["principioActivo"] or ""
            )

            self.txt_fabricante.setText(
                medicamento["fabricante"] or ""
            )

            self.txt_contenido.setText(
                medicamento["contenido"] or ""
            )

            self.spn_precio_compra.setValue(
                float(
                    medicamento["precioCompra"] or 0
                )
            )

            self.spn_precio_venta.setValue(
                float(
                    medicamento["precioVenta"] or 0
                )
            )

            self.spn_stock_minimo.setValue(
                medicamento["stockMinimo"] or 0
            )


            id_ubicacion = medicamento[
                "idUbicacion"
            ]


            indice = self.cmb_ubicacion.findData(
                id_ubicacion
            )


            if indice >= 0:

                self.cmb_ubicacion.setCurrentIndex(
                    indice
                )

            else:

                self.cmb_ubicacion.setCurrentIndex(
                    0
                )


            return True

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el medicamento:\n{e}"
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
    # MODIFICAR
    # =========================================================

    def modificar_medicamento(self):

        if self.id_medicamento_seleccionado is None:

            QMessageBox.warning(
                self,
                "Seleccione un medicamento",
                "Seleccione un medicamento de la tabla."
            )

            return


        if not self.validar_formulario():
            return


        conexion = conectar()

        if conexion is None:
            return

        cursor = None


        try:

            cursor = conexion.cursor()


            consulta = """
                UPDATE medicamentos

                SET
                    nombre = %s,
                    presentacion = %s,
                    codigoBarras = %s,
                    descripcion = %s,
                    principioActivo = %s,
                    fabricante = %s,
                    contenido = %s,
                    precioCompra = %s,
                    precioVenta = %s,
                    stockMinimo = %s,
                    idUbicacion = %s,
                    lote = %s,
                    fechaCaducidad = %s

                WHERE idMedicamento = %s
            """


            datos = list(
                self.obtener_datos_formulario()
            )

            datos.pop(2)  # La edición conserva las existencias que administra Inventario.

            datos.append(
                self.id_medicamento_seleccionado
            )


            cursor.execute(
                consulta,
                datos
            )

            conexion.commit()


            QMessageBox.information(
                self,
                "Modificado",
                "El medicamento se modificó correctamente."
            )


            self.limpiar_formulario()

            self.cargar_medicamentos()


            return True

        except Exception as e:

            conexion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo modificar el medicamento:\n{e}"
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
    # DESACTIVAR
    # =========================================================

    def desactivar_medicamento(self):

        if self.id_medicamento_seleccionado is None:

            QMessageBox.warning(
                self,
                "Seleccione un medicamento",
                "Seleccione un medicamento de la tabla."
            )

            return


        if not self.estado_medicamento_seleccionado:

            QMessageBox.warning(
                self,
                "Medicamento inactivo",
                "Este medicamento ya se encuentra inactivo."
            )

            return


        respuesta = QMessageBox.question(
            self,
            "Desactivar medicamento",
            "¿Desea desactivar este medicamento?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )


        if (
            respuesta
            != QMessageBox.StandardButton.Yes
        ):
            return


        conexion = conectar()

        if conexion is None:
            return

        cursor = None


        try:

            cursor = conexion.cursor()


            consulta = """
                UPDATE medicamentos
                SET activo = FALSE
                WHERE idMedicamento = %s
            """


            cursor.execute(
                consulta,
                (
                    self.id_medicamento_seleccionado,
                )
            )

            conexion.commit()


            QMessageBox.information(
                self,
                "Desactivado",
                "El medicamento se desactivó correctamente."
            )


            self.limpiar_formulario()

            self.cargar_medicamentos()


        except Exception as e:

            conexion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo desactivar el medicamento:\n{e}"
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
    # REACTIVAR
    # =========================================================

    def reactivar_medicamento(self):

        if self.id_medicamento_seleccionado is None:

            QMessageBox.warning(
                self,
                "Seleccione un medicamento",
                "Seleccione un medicamento de la tabla."
            )

            return


        if self.estado_medicamento_seleccionado:

            QMessageBox.warning(
                self,
                "Medicamento activo",
                "Este medicamento ya se encuentra activo."
            )

            return


        respuesta = QMessageBox.question(
            self,
            "Reactivar medicamento",
            "¿Desea reactivar este medicamento?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )


        if (
            respuesta
            != QMessageBox.StandardButton.Yes
        ):
            return


        conexion = conectar()

        if conexion is None:
            return

        cursor = None


        try:

            cursor = conexion.cursor()


            consulta = """
                UPDATE medicamentos
                SET activo = TRUE
                WHERE idMedicamento = %s
            """


            cursor.execute(
                consulta,
                (
                    self.id_medicamento_seleccionado,
                )
            )

            conexion.commit()


            QMessageBox.information(
                self,
                "Reactivado",
                "El medicamento se reactivó correctamente."
            )


            self.limpiar_formulario()

            self.cargar_medicamentos()


        except Exception as e:

            conexion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo reactivar el medicamento:\n{e}"
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
    # VALIDAR FORMULARIO
    # =========================================================

    def validar_formulario(self):

        nombre = self.txt_nombre.text().strip()


        if not nombre:

            QMessageBox.warning(
                self,
                "Campo obligatorio",
                "Ingrese el nombre del medicamento."
            )

            self.txt_nombre.setFocus()

            return False


        return True


    # =========================================================
    # OBTENER DATOS
    # =========================================================

    def obtener_datos_formulario(self):

        codigo = self.txt_codigo.text().strip()

        if codigo == "":
            codigo = None


        presentacion = (
            self.txt_presentacion
            .text()
            .strip()
        )

        if presentacion == "":
            presentacion = None


        descripcion = (
            self.txt_descripcion
            .toPlainText()
            .strip()
        )

        if descripcion == "":
            descripcion = None


        principio = (
            self.txt_principio
            .text()
            .strip()
        )

        if principio == "":
            principio = None


        fabricante = (
            self.txt_fabricante
            .text()
            .strip()
        )

        if fabricante == "":
            fabricante = None


        contenido = (
            self.txt_contenido
            .text()
            .strip()
        )

        if contenido == "":
            contenido = None


        id_ubicacion = (
            self.cmb_ubicacion
            .currentData()
        )


        return (
            self.txt_nombre.text().strip(),
            presentacion,
            self.spn_cantidad.value(),
            codigo,
            descripcion,
            principio,
            fabricante,
            contenido,
            self.spn_precio_compra.value(),
            self.spn_precio_venta.value(),
            self.spn_stock_minimo.value(),
            id_ubicacion,
            self.txt_lote.text().strip() or None,
            None if self.sin_caducidad.isChecked() else self.fecha_caducidad.date().toPyDate()
        )


    # =========================================================
    # LIMPIAR
    # =========================================================

    def limpiar_formulario(self):
        self.spn_cantidad.setEnabled(True)
        self.spn_cantidad.setToolTip("")

        self.id_medicamento_seleccionado = None

        self.estado_medicamento_seleccionado = None


        self.txt_nombre.clear()

        self.txt_presentacion.clear()

        self.spn_cantidad.setValue(
            0
        )

        self.txt_lote.clear()
        self.sin_caducidad.setChecked(True)
        self.fecha_caducidad.setDate(QDate.currentDate())
        self.txt_codigo.clear()

        self.txt_descripcion.clear()

        self.txt_principio.clear()

        self.txt_fabricante.clear()

        self.txt_contenido.clear()

        self.spn_precio_compra.setValue(
            0
        )

        self.spn_precio_venta.setValue(
            0
        )

        self.spn_stock_minimo.setValue(
            5
        )

        self.cmb_ubicacion.setCurrentIndex(
            0
        )

        self.tabla.clearSelection()


        self.btn_modificar.setEnabled(
            False
        )

        self.btn_desactivar.setEnabled(
            False
        )

        self.btn_reactivar.setEnabled(
            False
        )


        self.txt_nombre.setFocus()
