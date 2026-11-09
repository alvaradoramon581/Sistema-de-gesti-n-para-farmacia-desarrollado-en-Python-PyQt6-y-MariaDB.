"""Instalación explícita e idempotente de las tablas de operaciones."""
from pathlib import Path
from conexion import conectar


def preparar_ficha_medicamento(cur):
    cur.execute('SHOW COLUMNS FROM medicamentos')
    columnas = {fila[0] for fila in cur.fetchall()}
    faltantes = [f'ADD COLUMN {nombre} {tipo} NULL'
                 for nombre, tipo in [('lote', 'VARCHAR(60)'), ('fechaCaducidad', 'DATE')]
                 if nombre not in columnas]
    if not faltantes:
        return

    cur.execute('ALTER TABLE medicamentos ' + ', '.join(faltantes))
    cur.execute("SHOW TABLES LIKE 'lotes'")
    if cur.fetchone():
        # Una fecha única solo representa al producto si cubre toda su existencia.
        # Con varios lotes se conserva el historial original para su revisión.
        cur.execute('''UPDATE medicamentos m JOIN (
                SELECT idMedicamento, MIN(codigo) AS codigo, MIN(fechaCaducidad) AS fecha,
                       SUM(cantidad) AS unidades
                FROM lotes WHERE cantidad>0 GROUP BY idMedicamento HAVING COUNT(*)=1
            ) anterior ON anterior.idMedicamento=m.idMedicamento AND anterior.unidades=m.cantidad
            SET m.lote=anterior.codigo, m.fechaCaducidad=anterior.fecha
            WHERE m.lote IS NULL AND m.fechaCaducidad IS NULL''')


def aplicar(conexion):
    sql = (Path(__file__).parent / 'database/002_operaciones.sql').read_text(encoding='utf-8')
    sql = '\n'.join(linea for linea in sql.splitlines() if not linea.lstrip().startswith('--'))
    cur = conexion.cursor()
    try:
        preparar_ficha_medicamento(cur)
        for sentencia in sql.split(';'):
            if sentencia.strip():
                cur.execute(sentencia)
        conexion.commit()
    finally:
        cur.close()


if __name__ == '__main__':
    conexion = conectar()
    if conexion is None:
        raise SystemExit('No se pudo conectar.')
    try:
        aplicar(conexion)
        print('Tablas de operaciones preparadas. Datos existentes conservados.')
    finally:
        conexion.close()
