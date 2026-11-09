from PyQt6.QtCore import Qt, QSize, QPointF
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (QSpinBox, QComboBox, QPlainTextEdit, QLabel, QWidget,
                             QHBoxLayout, QToolButton, QButtonGroup, QSizePolicy)
from listados import Listado,Formulario
from ui_comun import boton,manejar_errores,dimensionar_dialogo
from estilos import ESTILO_CARITAS
from servicios import transaccion,autorizar


CALIFICACIONES = ('Muy insatisfecho', 'Insatisfecho', 'Neutral', 'Satisfecho', 'Muy satisfecho')


def folio_encuesta(numero, fecha):
    return f'#{numero} · {fecha:%d/%m/%Y %H:%M:%S}'


def registrar_encuesta(usuario, calificacion, comentario, venta=None):
    numero, _ = registrar_encuesta_con_fecha(usuario, calificacion, comentario, venta)
    return numero


def registrar_encuesta_con_fecha(usuario,calificacion,comentario,venta=None):
    if type(calificacion) is not int or not 1<=calificacion<=5: raise ValueError('La calificación debe estar entre 1 y 5.')
    if len(comentario)>500: raise ValueError('El comentario admite hasta 500 caracteres.')
    with transaccion() as cur:
        actual=autorizar(cur,usuario,bloquear=True)
        if venta is not None:
            cur.execute('SELECT idUsuario FROM ventas WHERE idVenta=%s',(venta,))
            registro=cur.fetchone()
            if not registro or (actual['rol']!='ADMIN' and registro['idUsuario']!=usuario['idUsuario']):
                raise ValueError('La venta no existe o no pertenece a este usuario.')
        cur.execute('INSERT INTO encuestas (idVenta,calificacion,comentario) VALUES (%s,%s,%s)',
                    (venta,calificacion,comentario.strip() or None))
        encuesta=cur.lastrowid
        cur.execute('INSERT INTO encuesta_autor (idEncuesta,idUsuario) VALUES (%s,%s)',(encuesta,usuario['idUsuario']))
        cur.execute('SELECT fecha FROM encuestas WHERE idEncuesta=%s', (encuesta,))
        return encuesta, cur.fetchone()['fecha']


def listar_encuestas(usuario,texto='',calificacion=None):
    with transaccion() as cur:
        actual=autorizar(cur,usuario)
        sql='''SELECT e.*,u.nombre AS capturo FROM encuestas e
            LEFT JOIN encuesta_autor a ON a.idEncuesta=e.idEncuesta
            LEFT JOIN usuarios u ON u.idUsuario=a.idUsuario'''
        texto = texto.strip()
        numero = texto.removeprefix('#').partition(' · ')[0]
        if texto.startswith('#') and numero.isdecimal():
            sql += ' WHERE e.idEncuesta=%s'
            params = [numero]
        else:
            sql += " WHERE (COALESCE(e.comentario,'') LIKE %s OR CAST(e.idEncuesta AS CHAR) LIKE %s)"
            params = ['%' + texto + '%'] * 2
        if actual['rol']!='ADMIN':
            sql+=' AND a.idUsuario=%s'; params.append(usuario['idUsuario'])
        if calificacion is not None:
            sql+=' AND e.calificacion=%s'; params.append(calificacion)
        cur.execute(sql+' ORDER BY e.fecha DESC,e.idEncuesta DESC',params)
        return cur.fetchall()


def icono_carita(numero):
    colores = ('#F2A79B', '#F5BD90', '#F4D790', '#B9DDA9', '#8FD1B5')
    imagen = QPixmap(96, 96)
    imagen.fill(Qt.GlobalColor.transparent)
    dibujo = QPainter(imagen)
    dibujo.setRenderHint(QPainter.RenderHint.Antialiasing)
    tinta = QColor('#33444C')
    dibujo.setPen(QPen(tinta, 3))
    dibujo.setBrush(QColor(colores[numero - 1]))
    dibujo.drawEllipse(6, 6, 84, 84)
    dibujo.setBrush(tinta)
    for x in (33, 63):
        dibujo.drawEllipse(QPointF(x, 36), 3, 4)
    # El centro de la boca sube en las caras tristes y baja en las sonrientes.
    curva = (numero - 3) * 7
    boca = QPainterPath(QPointF(28, 62 - curva / 2))
    boca.quadTo(48, 62 + curva * 1.5, 68, 62 - curva / 2)
    dibujo.setPen(QPen(tinta, 4, cap=Qt.PenCapStyle.RoundCap))
    dibujo.setBrush(Qt.BrushStyle.NoBrush)
    dibujo.drawPath(boca)
    dibujo.end()
    return QIcon(imagen)


class DialogoEncuesta(Formulario):
    def __init__(self,usuario,registro=None,parent=None):
        super().__init__('Consultar encuesta' if registro else 'Registrar encuesta',parent)
        dimensionar_dialogo(self, 725, 455)
        self.usuario=usuario
        self.folio = folio_encuesta(registro['idEncuesta'], registro['fecha']) if registro else None
        self.form.addRow('Folio de encuesta', QLabel(self.folio or 'Se asigna al guardar.'))
        self.venta=QSpinBox(); self.venta.setRange(0,2147483647); self.venta.setSpecialValueText('Sin venta asociada')
        selector = QWidget()
        fila = QHBoxLayout(selector)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(6)
        selector.setStyleSheet(ESTILO_CARITAS)
        self.calificacion = QButtonGroup(self)
        for numero, texto in enumerate(CALIFICACIONES, 1):
            cara = QToolButton()
            cara.setIcon(icono_carita(numero))
            cara.setIconSize(QSize(40, 40))
            cara.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            cara.setText(texto)
            cara.setAccessibleName(texto)
            cara.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            cara.setCheckable(True)
            self.calificacion.addButton(cara, numero)
            fila.addWidget(cara, 1)
        self.comentario=QPlainTextEdit(); self.comentario.setPlaceholderText('Comentario opcional, máximo 500 caracteres')
        self.comentario.setMaximumHeight(95)
        self.form.addRow('Folio de venta (opcional)',self.venta)
        self.form.addRow(QLabel('Calificación *'))
        self.form.addRow(selector)
        self.form.addRow('Comentario',self.comentario)
        if registro:
            self.venta.setValue(registro['idVenta'] or 0)
            self.calificacion.button(registro['calificacion']).setChecked(True)
            self.comentario.setPlainText(registro['comentario'] or '')
            self.venta.setEnabled(False); selector.setEnabled(False); self.comentario.setReadOnly(True)
        else: self.guardar_boton(self.guardar)

    @manejar_errores
    def guardar(self):
        nota = self.calificacion.checkedId()
        if nota < 1:
            raise ValueError('Seleccione una carita para calificar la atención.')
        numero, fecha = registrar_encuesta_con_fecha(
            self.usuario, nota, self.comentario.toPlainText(), self.venta.value() or None)
        self.folio = folio_encuesta(numero, fecha)
        self.accept()


class Encuestas(Listado):
    def __init__(self,usuario):
        super().__init__(usuario,'Encuestas de satisfacción',['Folio de encuesta','Venta','Calificación','Comentario','Capturó'],
                         'Registre la opinión del cliente, con venta asociada o sin ella.')
        self.calificacion=QComboBox(); self.calificacion.addItem('Todas las calificaciones',None)
        self.busqueda.setPlaceholderText('Buscar por folio o comentario…')
        for i in range(1,6): self.calificacion.addItem(str(i),i)
        self.filtros.insertWidget(0,self.calificacion)
        self.calificacion.currentIndexChanged.connect(self.recargar)
        self.acciones.addWidget(boton('Registrar encuesta',self.nueva))
        self.acciones.addWidget(boton('Consultar',self.consultar,True))
        self.tabla.cellDoubleClicked.connect(self.consultar)

    @manejar_errores
    def recargar(self,*_):
        self.limpiar()
        registros=listar_encuestas(self.usuario,self.busqueda.text(),self.calificacion.currentData())
        self.mostrar(registros,[(folio_encuesta(r['idEncuesta'],r['fecha']),r['idVenta'] or 'Sin venta',r['calificacion'],
            (r['comentario'] or '').replace('\n',' ')[:100],r['capturo'] or 'Registro anterior') for r in registros])
        promedio=sum(r['calificacion'] for r in registros)/len(registros) if registros else 0
        self.resumen.setText(f'{len(registros)} encuesta(s). Promedio de la lista: {promedio:.2f} / 5.')

    @manejar_errores
    def nueva(self):
        dialogo = DialogoEncuesta(self.usuario, parent=self)
        if dialogo.exec():
            self.recargar()
            self.resumen.setText(f'Encuesta registrada. Folio {dialogo.folio}.   {self.resumen.text()}')

    @manejar_errores
    def consultar(self,*_):
        seleccion=self.seleccionado()
        vigentes=listar_encuestas(self.usuario, folio_encuesta(seleccion['idEncuesta'], seleccion['fecha']))
        registro=next((r for r in vigentes if r['idEncuesta']==seleccion['idEncuesta']),None)
        if not registro: raise ValueError('La encuesta ya no está disponible para este usuario.')
        DialogoEncuesta(self.usuario,registro,self).exec()
