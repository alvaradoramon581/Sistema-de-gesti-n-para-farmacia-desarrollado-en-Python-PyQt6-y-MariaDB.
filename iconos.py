"""Pictogramas vectoriales de la farmacia, dibujados con el motor SVG de Qt."""
from pathlib import Path
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QBitmap, QColor, QIcon, QImage, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer


TRAZOS = {
    'Farmacia': '<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z"/>',
    'Inicio': '<path d="m3 11 9-8 9 8M5 10v11h5v-7h4v7h5V10"/>',
    'Buscar medicamento': '<circle cx="10" cy="10" r="6.5"/><path d="m15 15 6 6"/>',
    'Medicamentos': '<path d="M4.5 19.5a5.7 5.7 0 0 1 0-8l7-7a5.7 5.7 0 0 1 8 8l-7 7a5.7 5.7 0 0 1-8 0ZM8 8l8 8"/>',
    'Ventas': '<path d="M5 3h14v18l-3-2-4 2-4-2-3 2zM8 8h8M8 12h6"/>',
    'Inventario': '<path d="m3 7 9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10M7 5l9 4"/>',
    'Empleados': '<circle cx="9" cy="8" r="3"/><path d="M2 20v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6M17 14a5 5 0 0 1 5 5"/>',
    'Reportes': '<path d="M4 3v17h17M8 16v-5m5 5V6m5 10V9"/>',
    'Encuestas': '<rect x="3" y="4" width="18" height="16" rx="4"/><path d="M8 13q4 5 8 0M8 9h.5m7 0h.5"/>',
    'Alertas': '<path d="M4 17h16l-2-3v-4a6 6 0 0 0-12 0v4zM10 20q2 2 4 0"/>',
    'Perfil': '<circle cx="12" cy="8" r="3.5"/><path d="M4 21v-2a8 7 0 0 1 16 0v2"/>',
    'Calendario': '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M7 3v5m10-5v5M3 11h18m-12 4h3"/>',
    'Cerrar sesión': '<path d="M11 4H4v16h7M9 12h12m-5-5 5 5-5 5"/>',
}


def _pixmap(svg, ancho, alto):
    # Renderizar al doble conserva los contornos nítidos en pantallas con escalado.
    imagen = QPixmap(ancho * 2, alto * 2)
    imagen.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(imagen)
    QSvgRenderer(svg.encode('utf-8')).render(pintor)
    pintor.end()
    imagen.setDevicePixelRatio(2)
    return imagen


def icono(nombre, color='#DCEEFF', tamano=20):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
           f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
           f'{TRAZOS[nombre]}</svg>')
    return QIcon(_pixmap(svg, tamano, tamano))


def imagen_logo(tamano: QSize, solo_simbolo=False, fondo=None):
    original = QPixmap(str(Path(__file__).with_name('Logo.jpeg')))
    if original.isNull():
        return icono('Farmacia', '#1565A5').pixmap(tamano, 2)

    if solo_simbolo:
        # El final de la ola queda entre la F y el punto de la i del rótulo.
        imagen = QPixmap(864, 588)
        imagen.fill(Qt.GlobalColor.white)
        pintor = QPainter(imagen)
        pintor.drawPixmap(0, 0, original, 288, 66, 864, 558)
        pintor.drawPixmap(122, 558, original, 410, 624, 652, 30)
        pintor.end()
        # Unificar los blancos del JPEG antes de quitar el fondo exterior.
        silueta = imagen.toImage().convertToFormat(QImage.Format.Format_Indexed8,
                                                    Qt.ImageConversionFlag.ThresholdDither)
        imagen.setMask(QBitmap.fromImage(silueta.createHeuristicMask()))
    else:
        # Quitar el margen exterior del JPEG conservando el nombre y el lema.
        imagen = original.copy(QRect(254, 62, 1028, 880))
    resultado = imagen.scaled(tamano * 2, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
    if fondo:
        pintor = QPainter(resultado)
        pintor.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
        pintor.fillRect(resultado.rect(), QColor(fondo))
        pintor.end()
    resultado.setDevicePixelRatio(2)
    return resultado
