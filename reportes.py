import csv
from datetime import date
from pathlib import Path
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QComboBox,QDateEdit,QLabel,QFileDialog,QMessageBox,QHBoxLayout
from listados import Listado
from ui_comun import boton,manejar_errores
from servicios import transaccion,autorizar
from encuestas import CALIFICACIONES, folio_encuesta

TIPOS=['Ventas','Ventas por usuario','Encuestas','Inventario','Empleados']
TIPOS_PERSONALES = ['Ventas', 'Ventas por usuario', 'Encuestas']


def vendedores(usuario):
    with transaccion() as cur:
        actual = autorizar(cur, usuario)
        if actual['rol'] == 'ADMIN':
            cur.execute('SELECT idUsuario,nombre FROM usuarios ORDER BY nombre')
        else:
            cur.execute('SELECT idUsuario,nombre FROM usuarios WHERE idUsuario=%s', (actual['idUsuario'],))
        return cur.fetchall()


def generar_reporte(usuario,tipo,desde,hasta,vendedor=None):
    if tipo not in TIPOS: raise ValueError('Seleccione un reporte válido.')
    if type(desde) is not date or type(hasta) is not date or desde>hasta: raise ValueError('Revise el rango de fechas.')
    with transaccion() as cur:
        actual = autorizar(cur, usuario)
        if actual['rol'] != 'ADMIN':
            if tipo not in TIPOS_PERSONALES:
                raise ValueError('Solo puede generar reportes de sus propias ventas y encuestas.')
            if vendedor is not None and vendedor != actual['idUsuario']:
                raise ValueError('Solo puede generar reportes de sus propias ventas y encuestas.')
            vendedor = actual['idUsuario']
        if tipo in ('Ventas','Ventas por usuario'):
            filtro='v.fecha >= %s AND v.fecha < DATE_ADD(%s,INTERVAL 1 DAY)'
            params=[desde,hasta]
            if vendedor is not None: filtro+=' AND v.idUsuario=%s'; params.append(vendedor)
            if tipo=='Ventas':
                columnas=['Folio','Fecha','Vendedor','Método de pago','Subtotal','Total']
                sql='''SELECT v.idVenta,v.fecha,u.nombre,v.metodoPago,v.subtotal,v.total
                    FROM ventas v JOIN usuarios u ON u.idUsuario=v.idUsuario WHERE '''+filtro+' ORDER BY v.fecha,v.idVenta'
            else:
                columnas=['ID usuario','Vendedor','Número de ventas','Total vendido','Venta promedio']
                sql='''SELECT u.idUsuario,u.nombre,COUNT(v.idVenta),SUM(v.total),AVG(v.total)
                    FROM ventas v JOIN usuarios u ON u.idUsuario=v.idUsuario WHERE '''+filtro+' GROUP BY u.idUsuario,u.nombre ORDER BY u.nombre'
        elif tipo == 'Encuestas':
            columnas = ['Folio de encuesta', 'Fecha', 'Folio de venta', 'Calificación', 'Satisfacción', 'Comentario', 'Capturó']
            sql = '''SELECT e.idEncuesta, e.fecha, e.idVenta, e.calificacion, e.comentario,
                            COALESCE(u.nombre, 'Registro anterior') AS capturo
                     FROM encuestas e
                     LEFT JOIN encuesta_autor a ON a.idEncuesta=e.idEncuesta
                     LEFT JOIN usuarios u ON u.idUsuario=a.idUsuario
                     WHERE e.fecha >= %s AND e.fecha < DATE_ADD(%s, INTERVAL 1 DAY)'''
            params = [desde, hasta]
            if vendedor is not None:
                sql += ' AND a.idUsuario=%s'
                params.append(vendedor)
            cur.execute(sql + ' ORDER BY e.fecha, e.idEncuesta', params)
            filas = [[folio_encuesta(r['idEncuesta'], r['fecha']), r['fecha'],
                      r['idVenta'] if r['idVenta'] is not None else 'Sin venta',
                      r['calificacion'], CALIFICACIONES[r['calificacion'] - 1],
                      r['comentario'] or '', r['capturo']] for r in cur.fetchall()]
            return columnas, filas
        elif tipo=='Inventario':
            columnas=['ID','Medicamento','Proveedor','Lote','Caducidad','Existencia total','Mínimo','Precio venta','Valor a costo','Estado']
            sql='''SELECT m.idMedicamento,m.nombre,m.proveedor,m.lote,m.fechaCaducidad,m.cantidad,m.stockMinimo,m.precioVenta,
                m.cantidad*m.precioCompra,IF(m.activo=1,'Activo','Inactivo') FROM medicamentos m
                ORDER BY m.nombre'''; params=[]
        else:
            columnas=['ID','Nombre','RFC','Teléfono','Usuario','Rol','Estado']
            sql='''SELECT e.idEmpleado,e.nombre,e.rfc,e.telefono,u.usuario,u.rol,IF(e.activo=1,'Activo','Inactivo')
                FROM empleados e LEFT JOIN usuarios u ON u.idUsuario=e.idUsuario ORDER BY e.nombre'''; params=[]
        # Cursor normal para mantener encabezados explícitos y orden de columnas.
        cur.execute(sql,params)
        filas=[list(r.values()) for r in cur.fetchall()]
        return columnas,filas


def exportar_csv(ruta,columnas,filas):
    def celda(valor):
        # Evitar fórmulas al abrir nombres/comentarios como CSV en una hoja de cálculo.
        if isinstance(valor,str) and valor.lstrip().startswith(('=','+','-','@','\t','\r')): return "'"+valor
        return '' if valor is None else valor
    try:
        with Path(ruta).open('w',encoding='utf-8-sig',newline='') as archivo:
            escritor=csv.writer(archivo,delimiter=';')
            escritor.writerow(columnas)
            escritor.writerows([[celda(v) for v in fila] for fila in filas])
    except OSError as exc:
        raise ValueError('No se pudo guardar el archivo. Revise la carpeta o cierre el archivo si está abierto.') from exc


class Reportes(Listado):
    def __init__(self,usuario):
        super().__init__(usuario,'Reportes',['Resultado'],'Seleccione un reporte y consulte o exporte sus resultados.')
        self.busqueda.hide()
        self.tipo=QComboBox()
        self.tipo.addItems(TIPOS if usuario.get('rol') == 'ADMIN' else TIPOS_PERSONALES)
        self.desde=QDateEdit(QDate.currentDate().addMonths(-1)); self.hasta=QDateEdit(QDate.currentDate())
        self.vendedor=QComboBox()
        if usuario.get('rol') == 'ADMIN':
            self.vendedor.addItem('Todos los usuarios', None)
        else:
            self.vendedor.addItem(usuario['nombre'], usuario['idUsuario'])
        for campo in [self.desde,self.hasta]: campo.setCalendarPopup(True); campo.setDisplayFormat('dd/MM/yyyy')
        self.filtros.insertWidget(0,self.tipo)
        self.filtros.insertWidget(1, QLabel('Usuario'))
        self.filtros.insertWidget(2, self.vendedor, 1)
        fechas = QHBoxLayout()
        for etiqueta, campo in [('Desde', self.desde), ('Hasta', self.hasta)]:
            fechas.addWidget(QLabel(etiqueta))
            fechas.addWidget(campo)
        fechas.addStretch()
        self.panel_filtros.layout().addLayout(fechas)
        self.nota = QLabel('')
        self.nota.setWordWrap(True)
        self.panel_filtros.layout().addWidget(self.nota)
        self.acciones.addWidget(boton('Generar reporte',self.recargar))
        self.acciones.addWidget(boton('Exportar CSV',self.exportar,True))
        self.tipo.currentIndexChanged.connect(self.cambiar_tipo)
        self.desde.dateChanged.connect(self.limpiar)
        self.hasta.dateChanged.connect(self.limpiar)
        self.vendedor.currentIndexChanged.connect(self.limpiar)
        self.cambiar_tipo()

    def cambiar_tipo(self,*_):
        temporal=self.tipo.currentText() not in ('Empleados','Inventario')
        self.desde.setEnabled(temporal); self.hasta.setEnabled(temporal)
        self.vendedor.setEnabled(self.usuario.get('rol') == 'ADMIN' and temporal)
        self.nota.setText('El rango incluye ambas fechas.' if temporal else 'Estado actual. Las fechas no se aplican a este reporte.')
        self.limpiar()

    @manejar_errores
    def preparar(self):
        self.vendedor.blockSignals(True)
        self.vendedor.clear()
        try:
            if self.usuario.get('rol') == 'ADMIN':
                self.vendedor.addItem('Todos los usuarios', None)
            for u in vendedores(self.usuario): self.vendedor.addItem(u['nombre'],u['idUsuario'])
        finally: self.vendedor.blockSignals(False)
        self.recargar()

    def datos(self):
        return generar_reporte(self.usuario,self.tipo.currentText(),self.desde.date().toPyDate(),
                               self.hasta.date().toPyDate(),self.vendedor.currentData())

    @manejar_errores
    def recargar(self,*_):
        self.limpiar()
        columnas,filas=self.datos()
        self.tabla.setColumnCount(len(columnas)); self.tabla.setHorizontalHeaderLabels(columnas)
        self.mostrar(filas,filas)

    @manejar_errores
    def exportar(self):
        columnas,filas=self.datos()  # Revalidar permisos y regenerar los datos.
        ruta,_=QFileDialog.getSaveFileName(self,'Exportar reporte',self.tipo.currentText()+'.csv','CSV (*.csv)')
        if ruta:
            exportar_csv(ruta,columnas,filas)
            QMessageBox.information(self,'Reporte exportado','El reporte se guardó correctamente.')
