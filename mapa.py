# mapa.py

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsPolygonItem,
    QGraphicsTextItem,
    QMessageBox
)

from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPointF
)

from PyQt6.QtGui import (
    QColor,
    QBrush,
    QPen,
    QFont,
    QPolygonF
)

from conexion import conectar


class MapaMedicamentos(QWidget):

    def __init__(self):
        super().__init__()

        # =====================================================
        # SELECCIÓN ACTUAL
        # =====================================================

        self.id_medicamento_seleccionado = None
        self.id_ubicacion_seleccionada = None
        self.nivel_seleccionado = None

        # =====================================================
        # ESTANTES
        # =====================================================

        self.estantes = {}

        # Los estantes tienen 4 niveles
        self.total_niveles = 4

        # =====================================================
        # SEPARACIÓN ENTRE ESTANTES
        # =====================================================

        self.factor_separacion_x = 1.35
        self.factor_separacion_y = 1.55

        # =====================================================
        # PARPADEO
        # =====================================================

        self.estado_parpadeo = False

        self.timer_parpadeo = QTimer()

        self.timer_parpadeo.setInterval(
            450
        )

        self.timer_parpadeo.timeout.connect(
            self.parpadear_nivel
        )

        # =====================================================
        # INTERFAZ
        # =====================================================

        self.crear_interfaz()

        self.cargar_mapa()

        self.buscar_medicamentos()


    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(
            self
        )

        layout_principal.setContentsMargins(
            30,
            25,
            30,
            25
        )

        layout_principal.setSpacing(
            15
        )

        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = QLabel(
            "Localizar medicamento"
        )

        titulo.setStyleSheet("""
            QLabel {
                color: #1565C0;
                background-color: transparent;

                font-size: 28px;
                font-weight: bold;
            }
        """)

        descripcion = QLabel(
            "Busque un medicamento para visualizar "
            "el estante y nivel donde se encuentra."
        )

        descripcion.setStyleSheet("""
            QLabel {
                color: #607D8B;
                background-color: transparent;

                font-size: 14px;
            }
        """)

        # =====================================================
        # BUSCADOR
        # =====================================================

        layout_busqueda = QHBoxLayout()

        self.txt_buscar = QLineEdit()

        self.txt_buscar.setPlaceholderText(
            "Nombre, código de barras, principio activo "
            "o fabricante..."
        )

        self.txt_buscar.textChanged.connect(
            self.buscar_medicamentos
        )

        self.txt_buscar.returnPressed.connect(
            self.seleccionar_primer_resultado
        )

        self.btn_buscar = QPushButton(
            "Buscar"
        )

        self.btn_buscar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_buscar.clicked.connect(
            self.buscar_medicamentos
        )

        self.btn_limpiar = QPushButton(
            "Limpiar"
        )

        self.btn_limpiar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_busqueda
        )

        layout_busqueda.addWidget(
            self.txt_buscar,
            1
        )

        layout_busqueda.addWidget(
            self.btn_buscar
        )

        layout_busqueda.addWidget(
            self.btn_limpiar
        )

        # =====================================================
        # CUERPO
        # =====================================================

        layout_cuerpo = QHBoxLayout()

        layout_cuerpo.setSpacing(
            15
        )

        # =====================================================
        # PANEL IZQUIERDO
        # =====================================================

        panel_izquierdo = QFrame()

        panel_izquierdo.setObjectName(
            "panelInformacion"
        )

        panel_izquierdo.setMinimumWidth(
            330
        )

        panel_izquierdo.setMaximumWidth(
            420
        )

        panel_izquierdo.setStyleSheet("""
            QFrame#panelInformacion {
                background-color: #FFFFFF;

                border: 1px solid #D6E4F0;
                border-radius: 10px;
            }
        """)

        layout_izquierdo = QVBoxLayout(
            panel_izquierdo
        )

        layout_izquierdo.setContentsMargins(
            15,
            15,
            15,
            15
        )

        layout_izquierdo.setSpacing(
            10
        )

        # =====================================================
        # RESULTADOS
        # =====================================================

        lbl_resultados = QLabel(
            "Resultados"
        )

        lbl_resultados.setStyleSheet("""
            QLabel {
                color: #37474F;
                background-color: transparent;

                font-size: 16px;
                font-weight: bold;
            }
        """)

        self.tabla_resultados = QTableWidget()

        self.tabla_resultados.setColumnCount(
            3
        )

        self.tabla_resultados.setHorizontalHeaderLabels([
            "Medicamento",
            "Existencia",
            "Ubicación"
        ])

        self.tabla_resultados.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabla_resultados.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabla_resultados.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabla_resultados.verticalHeader().setVisible(
            False
        )

        self.tabla_resultados.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla_resultados.cellClicked.connect(
            self.seleccionar_resultado
        )

        # =====================================================
        # INFORMACIÓN
        # =====================================================

        lbl_detalles = QLabel(
            "Información"
        )

        lbl_detalles.setStyleSheet("""
            QLabel {
                color: #37474F;
                background-color: transparent;

                font-size: 16px;
                font-weight: bold;

                margin-top: 5px;
            }
        """)

        self.lbl_nombre = QLabel(
            "Seleccione un medicamento"
        )

        self.lbl_nombre.setWordWrap(
            True
        )

        self.lbl_nombre.setStyleSheet("""
            QLabel {
                color: #1565C0;
                background-color: transparent;

                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.lbl_presentacion = QLabel(
            "Presentación: -"
        )

        self.lbl_existencia = QLabel(
            "Existencia: -"
        )

        self.lbl_principio = QLabel(
            "Principio activo: -"
        )

        self.lbl_fabricante = QLabel(
            "Fabricante: -"
        )

        self.lbl_ubicacion = QLabel(
            "Ubicación: -"
        )

        self.lbl_nivel = QLabel(
            "Nivel: -"
        )

        labels_info = [
            self.lbl_presentacion,
            self.lbl_existencia,
            self.lbl_principio,
            self.lbl_fabricante,
            self.lbl_ubicacion,
            self.lbl_nivel
        ]

        for label in labels_info:

            label.setWordWrap(
                True
            )

            label.setStyleSheet("""
                QLabel {
                    color: #455A64;
                    background-color: transparent;

                    font-size: 13px;
                }
            """)

        # =====================================================
        # ESTADO
        # =====================================================

        self.lbl_estado = QLabel(
            "Seleccione un resultado para localizarlo."
        )

        self.lbl_estado.setWordWrap(
            True
        )

        self.lbl_estado.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                color: #1565C0;

                border-radius: 6px;

                padding: 10px;

                font-weight: bold;
            }
        """)

        # =====================================================
        # AGREGAR PANEL IZQUIERDO
        # =====================================================

        layout_izquierdo.addWidget(
            lbl_resultados
        )

        layout_izquierdo.addWidget(
            self.tabla_resultados,
            1
        )

        layout_izquierdo.addWidget(
            lbl_detalles
        )

        layout_izquierdo.addWidget(
            self.lbl_nombre
        )

        layout_izquierdo.addWidget(
            self.lbl_presentacion
        )

        layout_izquierdo.addWidget(
            self.lbl_existencia
        )

        layout_izquierdo.addWidget(
            self.lbl_principio
        )

        layout_izquierdo.addWidget(
            self.lbl_fabricante
        )

        layout_izquierdo.addWidget(
            self.lbl_ubicacion
        )

        layout_izquierdo.addWidget(
            self.lbl_nivel
        )

        layout_izquierdo.addWidget(
            self.lbl_estado
        )

        # =====================================================
        # PANEL MAPA
        # =====================================================

        panel_mapa = QFrame()

        panel_mapa.setObjectName(
            "panelMapa"
        )

        panel_mapa.setStyleSheet("""
            QFrame#panelMapa {
                background-color: #FFFFFF;

                border: 1px solid #D6E4F0;
                border-radius: 10px;
            }
        """)

        layout_mapa = QVBoxLayout(
            panel_mapa
        )

        layout_mapa.setContentsMargins(
            15,
            15,
            15,
            15
        )

        titulo_mapa = QLabel(
            "Mapa de la farmacia"
        )

        titulo_mapa.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        titulo_mapa.setStyleSheet("""
            QLabel {
                color: #37474F;
                background-color: transparent;

                font-size: 18px;
                font-weight: bold;
            }
        """)

        leyenda = QLabel(
            "Estantes de 4 niveles  |  "
            "Nivel localizado en verde"
        )

        leyenda.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        leyenda.setStyleSheet("""
            QLabel {
                color: #607D8B;
                background-color: transparent;

                font-size: 12px;
            }
        """)

        # =====================================================
        # ESCENA
        # =====================================================

        self.scene = QGraphicsScene()

        self.vista = QGraphicsView(
            self.scene
        )

        self.vista.setStyleSheet("""
            QGraphicsView {
                background-color: #FAFCFE;

                border: 1px solid #CFD8DC;
                border-radius: 6px;
            }
        """)

        self.vista.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.vista.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        layout_mapa.addWidget(
            titulo_mapa
        )

        layout_mapa.addWidget(
            leyenda
        )

        layout_mapa.addWidget(
            self.vista,
            1
        )

        # =====================================================
        # CUERPO
        # =====================================================

        layout_cuerpo.addWidget(
            panel_izquierdo
        )

        layout_cuerpo.addWidget(
            panel_mapa,
            1
        )

        # =====================================================
        # PRINCIPAL
        # =====================================================

        layout_principal.addWidget(
            titulo
        )

        layout_principal.addWidget(
            descripcion
        )

        layout_principal.addLayout(
            layout_busqueda
        )

        layout_principal.addLayout(
            layout_cuerpo,
            1
        )


    # =========================================================
    # DIBUJAR ESTANTE
    # =========================================================

    def dibujar_estante(
        self,
        id_ubicacion,
        codigo,
        x,
        y,
        ancho,
        alto
    ):

        # =====================================================
        # TAMAÑO
        # =====================================================

        ancho = max(
            ancho,
            105
        )

        alto = max(
            alto,
            145
        )

        profundidad = 12

        grosor_lateral = 8

        # =====================================================
        # COLORES
        # =====================================================

        color_frente = QColor(
            "#ECEFF1"
        )

        color_lateral = QColor(
            "#B0BEC5"
        )

        color_sombra = QColor(
            "#90A4AE"
        )

        color_repisas = QColor(
            "#CFD8DC"
        )

        color_borde = QColor(
            "#78909C"
        )

        estructura = []

        niveles = {}

        # =====================================================
        # FONDO
        # =====================================================

        fondo = QGraphicsRectItem(
            x + grosor_lateral,
            y + grosor_lateral,
            ancho - (grosor_lateral * 2),
            alto - (grosor_lateral * 2)
        )

        fondo.setBrush(
            QBrush(
                QColor("#FAFAFA")
            )
        )

        fondo.setPen(
            QPen(
                QColor("#CFD8DC"),
                1
            )
        )

        self.scene.addItem(
            fondo
        )

        estructura.append(
            fondo
        )

        # =====================================================
        # LATERAL IZQUIERDO
        # =====================================================

        poligono_izquierdo = QPolygonF([
            QPointF(
                x,
                y
            ),
            QPointF(
                x + grosor_lateral,
                y + profundidad
            ),
            QPointF(
                x + grosor_lateral,
                y + alto
            ),
            QPointF(
                x,
                y + alto - profundidad
            )
        ])

        lateral_izquierdo = QGraphicsPolygonItem(
            poligono_izquierdo
        )

        lateral_izquierdo.setBrush(
            QBrush(
                color_lateral
            )
        )

        lateral_izquierdo.setPen(
            QPen(
                color_borde,
                1
            )
        )

        self.scene.addItem(
            lateral_izquierdo
        )

        estructura.append(
            lateral_izquierdo
        )

        # =====================================================
        # LATERAL DERECHO
        # =====================================================

        poligono_derecho = QPolygonF([
            QPointF(
                x + ancho - grosor_lateral,
                y + profundidad
            ),
            QPointF(
                x + ancho,
                y
            ),
            QPointF(
                x + ancho,
                y + alto - profundidad
            ),
            QPointF(
                x + ancho - grosor_lateral,
                y + alto
            )
        ])

        lateral_derecho = QGraphicsPolygonItem(
            poligono_derecho
        )

        lateral_derecho.setBrush(
            QBrush(
                color_lateral
            )
        )

        lateral_derecho.setPen(
            QPen(
                color_borde,
                1
            )
        )

        self.scene.addItem(
            lateral_derecho
        )

        estructura.append(
            lateral_derecho
        )

        # =====================================================
        # PARTE SUPERIOR
        # =====================================================

        poligono_superior = QPolygonF([
            QPointF(
                x,
                y
            ),
            QPointF(
                x + profundidad,
                y - profundidad
            ),
            QPointF(
                x + ancho + profundidad,
                y - profundidad
            ),
            QPointF(
                x + ancho,
                y
            )
        ])

        superior = QGraphicsPolygonItem(
            poligono_superior
        )

        superior.setBrush(
            QBrush(
                color_frente
            )
        )

        superior.setPen(
            QPen(
                color_borde,
                1
            )
        )

        self.scene.addItem(
            superior
        )

        estructura.append(
            superior
        )

        # =====================================================
        # 4 NIVELES DENTRO DEL MUEBLE
        # =====================================================
        #
        # Dejamos margen arriba y abajo para evitar
        # que cualquier repisa salga de los laterales.
        #
        # Nivel 4 = parte superior
        # Nivel 1 = parte inferior
        # =====================================================

        margen_superior = 20

        margen_inferior = 22

        # Zona disponible dentro del mueble
        espacio_util = (
            alto
            - margen_superior
            - margen_inferior
        )

        # Se divide en cuatro partes
        separacion_niveles = (
            espacio_util
            / self.total_niveles
        )

        for indice in range(
            self.total_niveles
        ):

            # Nivel 4 arriba
            # Nivel 1 abajo
            nivel_numero = (
                self.total_niveles
                - indice
            )

            # La repisa queda dentro del mueble
            y_repisa = (
                y
                + margen_superior
                + ((indice + 1) * separacion_niveles)
                - profundidad
            )

            # =================================================
            # REPISA CON EFECTO DE PROFUNDIDAD
            # =================================================

            poligono_repisa = QPolygonF([
                QPointF(
                    x + grosor_lateral,
                    y_repisa
                ),

                QPointF(
                    x + ancho - grosor_lateral,
                    y_repisa
                ),

                QPointF(
                    x
                    + ancho
                    - grosor_lateral
                    - profundidad,
                    y_repisa + profundidad
                ),

                QPointF(
                    x
                    + grosor_lateral
                    + profundidad,
                    y_repisa + profundidad
                )
            ])

            repisa = QGraphicsPolygonItem(
                poligono_repisa
            )

            repisa.setBrush(
                QBrush(
                    color_repisas
                )
            )

            repisa.setPen(
                QPen(
                    color_borde,
                    1
                )
            )

            self.scene.addItem(
                repisa
            )

            niveles[
                nivel_numero
            ] = repisa

        # =====================================================
        # BASE
        # =====================================================

        base = QGraphicsRectItem(
            x,
            y + alto - 5,
            ancho,
            8
        )

        base.setBrush(
            QBrush(
                color_sombra
            )
        )

        base.setPen(
            QPen(
                color_borde,
                1
            )
        )

        self.scene.addItem(
            base
        )

        estructura.append(
            base
        )

        # =====================================================
        # NOMBRE DEL ESTANTE
        # =====================================================

        texto = QGraphicsTextItem(
            codigo
        )

        texto.setDefaultTextColor(
            QColor("#263238")
        )

        fuente = QFont()

        fuente.setBold(
            True
        )

        fuente.setPointSize(
            11
        )

        texto.setFont(
            fuente
        )

        texto.setPos(
            x + 10,
            y - 38
        )

        self.scene.addItem(
            texto
        )

        estructura.append(
            texto
        )

        # =====================================================
        # GUARDAR
        # =====================================================

        self.estantes[
            id_ubicacion
        ] = {
            "estructura": estructura,
            "niveles": niveles
        }


    # =========================================================
    # CARGAR MAPA
    # =========================================================

    def cargar_mapa(self):

        self.detener_parpadeo()

        self.scene.clear()

        self.estantes.clear()

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
                    nivel,
                    descripcion,
                    posicionX,
                    posicionY,
                    ancho,
                    alto

                FROM ubicaciones

                WHERE activo = TRUE

                ORDER BY codigo
            """

            cursor.execute(
                consulta
            )

            ubicaciones = cursor.fetchall()

            # =================================================
            # ENTRADA
            # =================================================

            texto_entrada = self.scene.addText(
                "ENTRADA"
            )

            texto_entrada.setDefaultTextColor(
                QColor("#1565C0")
            )

            fuente = QFont()

            fuente.setBold(
                True
            )

            fuente.setPointSize(
                12
            )

            texto_entrada.setFont(
                fuente
            )

            texto_entrada.setPos(
                30,
                20
            )

            # =================================================
            # DIBUJAR ESTANTES
            # =================================================

            for ubicacion in ubicaciones:

                x_visual = (
                    ubicacion["posicionX"]
                    * self.factor_separacion_x
                )

                y_visual = (
                    ubicacion["posicionY"]
                    * self.factor_separacion_y
                )

                self.dibujar_estante(
                    ubicacion["idUbicacion"],
                    ubicacion["codigo"],
                    x_visual,
                    y_visual,
                    ubicacion["ancho"],
                    ubicacion["alto"]
                )

            # =================================================
            # ESCENA
            # =================================================

            limites = self.scene.itemsBoundingRect()

            self.scene.setSceneRect(
                limites.adjusted(
                    -70,
                    -70,
                    70,
                    70
                )
            )

            self.ajustar_mapa()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el mapa:\n{e}"
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
    # AJUSTAR MAPA
    # =========================================================

    def ajustar_mapa(self):

        if not self.scene.items():
            return

        self.vista.fitInView(
            self.scene.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio
        )


    # =========================================================
    # REDIMENSIONAR
    # =========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        self.ajustar_mapa()


    # =========================================================
    # BUSCAR MEDICAMENTOS
    # =========================================================

    def buscar_medicamentos(self):

        filtro = (
            self.txt_buscar
            .text()
            .strip()
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
                SELECT
                    m.idMedicamento,
                    m.nombre,
                    m.presentacion,
                    m.cantidad,
                    m.codigoBarras,
                    m.principioActivo,
                    m.fabricante,
                    m.idUbicacion,

                    u.codigo AS codigoUbicacion,
                    u.pasillo,
                    u.estante,
                    u.nivel

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

                patron = (
                    f"%{filtro}%"
                )

                parametros = [
                    patron,
                    patron,
                    patron,
                    patron
                ]

            consulta += """
                ORDER BY m.nombre
                LIMIT 100
            """

            cursor.execute(
                consulta,
                parametros
            )

            medicamentos = cursor.fetchall()

            self.tabla_resultados.setRowCount(
                len(medicamentos)
            )

            for fila, medicamento in enumerate(
                medicamentos
            ):

                # =================================================
                # NOMBRE + ID OCULTO
                # =================================================

                item_nombre = QTableWidgetItem(
                    medicamento["nombre"] or ""
                )

                item_nombre.setData(
                    Qt.ItemDataRole.UserRole,
                    medicamento["idMedicamento"]
                )

                self.tabla_resultados.setItem(
                    fila,
                    0,
                    item_nombre
                )

                # =================================================
                # EXISTENCIA
                # =================================================

                self.tabla_resultados.setItem(
                    fila,
                    1,
                    QTableWidgetItem(
                        str(
                            medicamento["cantidad"]
                        )
                    )
                )

                # =================================================
                # UBICACIÓN
                # =================================================

                if medicamento["codigoUbicacion"]:

                    ubicacion_texto = (
                        f"{medicamento['codigoUbicacion']}"
                    )

                    if medicamento["nivel"]:

                        ubicacion_texto += (
                            f" / Nivel {medicamento['nivel']}"
                        )

                else:

                    ubicacion_texto = (
                        "Sin ubicación"
                    )

                self.tabla_resultados.setItem(
                    fila,
                    2,
                    QTableWidgetItem(
                        ubicacion_texto
                    )
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron buscar medicamentos:\n{e}"
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
    # ENTER
    # =========================================================

    def seleccionar_primer_resultado(self):

        if self.tabla_resultados.rowCount() == 0:
            return

        self.tabla_resultados.selectRow(
            0
        )

        self.seleccionar_resultado(
            0,
            0
        )


    # =========================================================
    # SELECCIONAR RESULTADO
    # =========================================================

    def seleccionar_resultado(
        self,
        fila,
        columna
    ):

        item_nombre = self.tabla_resultados.item(
            fila,
            0
        )

        if item_nombre is None:
            return

        id_medicamento = item_nombre.data(
            Qt.ItemDataRole.UserRole
        )

        if id_medicamento is None:
            return

        self.id_medicamento_seleccionado = (
            id_medicamento
        )

        self.cargar_medicamento(
            id_medicamento
        )


    # =========================================================
    # CARGAR MEDICAMENTO
    # =========================================================

    def cargar_medicamento(
        self,
        id_medicamento
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
                    m.idUbicacion,

                    u.codigo AS codigoUbicacion,
                    u.pasillo,
                    u.estante,
                    u.nivel

                FROM medicamentos m

                LEFT JOIN ubicaciones u
                ON m.idUbicacion = u.idUbicacion

                WHERE m.idMedicamento = %s
                AND m.activo = TRUE

                LIMIT 1
            """

            cursor.execute(
                consulta,
                (
                    id_medicamento,
                )
            )

            medicamento = cursor.fetchone()

            if medicamento is None:
                return

            # =================================================
            # INFORMACIÓN
            # =================================================

            self.lbl_nombre.setText(
                medicamento["nombre"]
            )

            self.lbl_presentacion.setText(
                "Presentación: "
                + (
                    medicamento["presentacion"]
                    or "-"
                )
            )

            self.lbl_existencia.setText(
                f"Existencia: {medicamento['cantidad']}"
            )

            self.lbl_principio.setText(
                "Principio activo: "
                + (
                    medicamento["principioActivo"]
                    or "-"
                )
            )

            self.lbl_fabricante.setText(
                "Fabricante: "
                + (
                    medicamento["fabricante"]
                    or "-"
                )
            )

            # =================================================
            # SIN UBICACIÓN
            # =================================================

            if medicamento["idUbicacion"] is None:

                self.id_ubicacion_seleccionada = None

                self.nivel_seleccionado = None

                self.lbl_ubicacion.setText(
                    "Ubicación: Sin ubicación asignada"
                )

                self.lbl_nivel.setText(
                    "Nivel: -"
                )

                self.lbl_estado.setText(
                    "Este medicamento todavía no tiene "
                    "una ubicación asignada."
                )

                self.detener_parpadeo()

                self.restaurar_estantes()

                return

            # =================================================
            # UBICACIÓN
            # =================================================

            self.id_ubicacion_seleccionada = (
                medicamento["idUbicacion"]
            )

            ubicacion_texto = (
                f"{medicamento['codigoUbicacion']} - "
                f"Pasillo {medicamento['pasillo']} / "
                f"Estante {medicamento['estante']}"
            )

            self.lbl_ubicacion.setText(
                f"Ubicación: {ubicacion_texto}"
            )

            self.lbl_nivel.setText(
                "Nivel: "
                + (
                    str(
                        medicamento["nivel"]
                    )
                    if medicamento["nivel"]
                    else "-"
                )
            )

            # =================================================
            # NIVEL
            # =================================================

            try:

                nivel = int(
                    medicamento["nivel"]
                )

            except (
                TypeError,
                ValueError
            ):

                nivel = 1

            nivel = max(
                1,
                min(
                    nivel,
                    self.total_niveles
                )
            )

            self.nivel_seleccionado = (
                nivel
            )

            self.lbl_estado.setText(
                f"Medicamento localizado en el "
                f"estante {medicamento['codigoUbicacion']}, "
                f"nivel {nivel}."
            )

            self.resaltar_nivel(
                medicamento["idUbicacion"],
                nivel
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo localizar el medicamento:\n{e}"
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
    # RESTAURAR ESTANTES
    # =========================================================

    def restaurar_estantes(self):

        color_normal = QColor(
            "#CFD8DC"
        )

        borde_normal = QColor(
            "#78909C"
        )

        for estante in self.estantes.values():

            for repisa in estante["niveles"].values():

                repisa.setBrush(
                    QBrush(
                        color_normal
                    )
                )

                repisa.setPen(
                    QPen(
                        borde_normal,
                        1
                    )
                )


    # =========================================================
    # RESALTAR NIVEL
    # =========================================================

    def resaltar_nivel(
        self,
        id_ubicacion,
        nivel
    ):

        self.detener_parpadeo()

        self.restaurar_estantes()

        estante = self.estantes.get(
            id_ubicacion
        )

        if estante is None:

            self.lbl_estado.setText(
                "La ubicación existe en la base de datos, "
                "pero no está dibujada en el mapa."
            )

            return

        repisa = estante["niveles"].get(
            nivel
        )

        if repisa is None:

            self.lbl_estado.setText(
                "El nivel indicado no existe en este estante."
            )

            return

        self.id_ubicacion_seleccionada = (
            id_ubicacion
        )

        self.nivel_seleccionado = (
            nivel
        )

        repisa.setBrush(
            QBrush(
                QColor("#43A047")
            )
        )

        repisa.setPen(
            QPen(
                QColor("#1B5E20"),
                3
            )
        )

        self.vista.centerOn(
            repisa
        )

        self.estado_parpadeo = True

        self.timer_parpadeo.start()


    # =========================================================
    # PARPADEAR
    # =========================================================

    def parpadear_nivel(self):

        if (
            self.id_ubicacion_seleccionada is None
            or self.nivel_seleccionado is None
        ):
            return

        estante = self.estantes.get(
            self.id_ubicacion_seleccionada
        )

        if estante is None:
            return

        repisa = estante["niveles"].get(
            self.nivel_seleccionado
        )

        if repisa is None:
            return

        self.estado_parpadeo = (
            not self.estado_parpadeo
        )

        if self.estado_parpadeo:

            repisa.setBrush(
                QBrush(
                    QColor("#43A047")
                )
            )

            repisa.setPen(
                QPen(
                    QColor("#1B5E20"),
                    3
                )
            )

        else:

            repisa.setBrush(
                QBrush(
                    QColor("#A5D6A7")
                )
            )

            repisa.setPen(
                QPen(
                    QColor("#43A047"),
                    2
                )
            )


    # =========================================================
    # DETENER PARPADEO
    # =========================================================

    def detener_parpadeo(self):

        if self.timer_parpadeo.isActive():

            self.timer_parpadeo.stop()

        self.estado_parpadeo = False


    # =========================================================
    # LIMPIAR
    # =========================================================

    def limpiar_busqueda(self):

        self.detener_parpadeo()

        self.restaurar_estantes()

        self.id_medicamento_seleccionado = None

        self.id_ubicacion_seleccionada = None

        self.nivel_seleccionado = None

        self.txt_buscar.clear()

        self.lbl_nombre.setText(
            "Seleccione un medicamento"
        )

        self.lbl_presentacion.setText(
            "Presentación: -"
        )

        self.lbl_existencia.setText(
            "Existencia: -"
        )

        self.lbl_principio.setText(
            "Principio activo: -"
        )

        self.lbl_fabricante.setText(
            "Fabricante: -"
        )

        self.lbl_ubicacion.setText(
            "Ubicación: -"
        )

        self.lbl_nivel.setText(
            "Nivel: -"
        )

        self.lbl_estado.setText(
            "Seleccione un resultado para localizarlo."
        )

        self.tabla_resultados.clearSelection()

        self.txt_buscar.setFocus()


    # =========================================================
    # RECARGAR
    # =========================================================

    def recargar(self):

        self.detener_parpadeo()

        self.id_ubicacion_seleccionada = None

        self.nivel_seleccionado = None

        self.cargar_mapa()

        self.buscar_medicamentos()