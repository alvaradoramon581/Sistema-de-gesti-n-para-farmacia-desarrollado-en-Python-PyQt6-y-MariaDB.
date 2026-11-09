from PyQt6.QtWidgets import QComboBox,QSpinBox,QLabel,QHBoxLayout
from PyQt6.QtGui import QColor
from listados import Listado
from ui_comun import manejar_errores
from servicios import transaccion,autorizar

DIAS_URGENTES = 7


def obtener_alertas(usuario,dias=90):
    if type(dias) is not int or not 1<=dias<=3650: raise ValueError('El plazo debe estar entre 1 y 3650 días.')
    with transaccion() as cur:
        autorizar(cur,usuario)
        cur.execute("""SELECT nombre, cantidad, stockMinimo, activo, lote, fechaCaducidad,
                         DATEDIFF(fechaCaducidad, CURDATE()) AS diasRestantes
                       FROM medicamentos
                       WHERE (activo=1 AND cantidad<=stockMinimo)
                          OR (cantidad>0 AND fechaCaducidad<=DATE_ADD(CURDATE(), INTERVAL %s DAY))
                          OR (activo=1 AND cantidad>0 AND fechaCaducidad IS NULL)
                       ORDER BY fechaCaducidad, nombre""", (dias,))
        alertas = []
        for medicamento in cur.fetchall():
            cantidad = medicamento['cantidad']
            restantes = medicamento['diasRestantes']
            ficha = dict(nombre=medicamento['nombre'], lote=medicamento['lote'] or '—',
                         fecha=medicamento['fechaCaducidad'], cantidad=cantidad)
            if medicamento['activo'] and cantidad <= medicamento['stockMinimo']:
                detalle = f"Mínimo: {medicamento['stockMinimo']}"
                if cantidad == 0:
                    detalle = f'Agotado. {detalle}'
                alertas.append(dict(ficha, tipo='Existencia baja', detalle=detalle, urgente=cantidad == 0))
            if cantidad <= 0:
                continue
            if restantes is None and medicamento['activo']:
                alertas.append(dict(ficha, tipo='Sin caducidad registrada', detalle='Capturar la fecha en Medicamentos',
                                    urgente=False))
            elif restantes is not None and restantes <= dias:
                if restantes <= 0:
                    alertas.append(dict(ficha, tipo='Caducado / vence hoy', detalle='Retirar de la venta', urgente=True))
                else:
                    detalle = 'Falta 1 día' if restantes == 1 else f'Faltan {restantes} días'
                    alertas.append(dict(ficha, tipo='Próxima caducidad', detalle=detalle,
                                        urgente=restantes <= DIAS_URGENTES))
        return sorted(alertas, key=lambda alerta: not alerta['urgente'])


class Alertas(Listado):
    def __init__(self,usuario):
        super().__init__(usuario,'Alertas',['Tipo','Medicamento','Lote','Caducidad','Unidades','Detalle'],
                         f'Se marcan como urgentes los agotados, los vencidos y los que vencen en {DIAS_URGENTES} días o menos.')
        self.tipo=QComboBox()
        self.tipo.addItems(['Todas','Existencia baja','Próxima caducidad','Caducado / vence hoy','Sin caducidad registrada'])
        self.dias=QSpinBox(); self.dias.setRange(1,3650); self.dias.setValue(90)
        criterios = QHBoxLayout()
        criterios.addWidget(QLabel('Tipo'))
        criterios.addWidget(self.tipo)
        criterios.addWidget(QLabel('Avisar con días:'))
        criterios.addWidget(self.dias)
        criterios.addStretch()
        self.panel_filtros.layout().insertLayout(0, criterios)
        self.tipo.currentIndexChanged.connect(self.recargar)
        self.dias.valueChanged.connect(self.recargar)

    @manejar_errores
    def recargar(self,*_):
        self.limpiar()
        registros=obtener_alertas(self.usuario,self.dias.value())
        texto=self.busqueda.text().strip().casefold()
        registros=[r for r in registros if (self.tipo.currentIndex()==0 or r['tipo']==self.tipo.currentText())
                   and texto in (r['nombre']+' '+r['lote']).casefold()]
        filas = []
        for r in registros:
            detalle = f"Urgente · {r['detalle']}" if r['urgente'] else r['detalle']
            filas.append((r['tipo'], r['nombre'], r['lote'], r['fecha'], r['cantidad'], detalle))
        self.mostrar(registros, filas)
        for fila, registro in enumerate(registros):
            if registro['urgente']:
                for columna in (0, 5):
                    item = self.tabla.item(fila, columna)
                    fuente = item.font()
                    fuente.setBold(True)
                    item.setFont(fuente)
                    item.setForeground(QColor('#A61B1B'))
