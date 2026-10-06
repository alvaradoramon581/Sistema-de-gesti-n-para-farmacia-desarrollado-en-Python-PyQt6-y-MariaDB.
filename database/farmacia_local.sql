-- ============================================================
-- PROYECTO FARMACIA
-- Base de datos: farmacia_local
-- Motor: MariaDB / MySQL
-- ============================================================


-- ============================================================
-- CREAR BASE DE DATOS
-- ============================================================

CREATE DATABASE IF NOT EXISTS farmacia_local
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE farmacia_local;


-- ============================================================
-- ELIMINAR VISTAS SI YA EXISTEN
-- ============================================================

DROP VIEW IF EXISTS vista_ventas_por_usuario;
DROP VIEW IF EXISTS vista_stock_bajo;
DROP VIEW IF EXISTS vista_medicamentos_ubicacion;


-- ============================================================
-- ELIMINAR TABLAS SI YA EXISTEN
-- ============================================================

DROP TABLE IF EXISTS movimientos_inventario;
DROP TABLE IF EXISTS encuestas;
DROP TABLE IF EXISTS detalle_venta;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS medicamentos;
DROP TABLE IF EXISTS ubicaciones;
DROP TABLE IF EXISTS empleados;
DROP TABLE IF EXISTS usuarios;


-- ============================================================
-- TABLA: usuarios
-- ============================================================

CREATE TABLE usuarios (

    idUsuario INT NOT NULL AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    usuario VARCHAR(50) NOT NULL,

    contrasena VARCHAR(255) NOT NULL,

    rol ENUM(
        'ADMIN',
        'EMPLEADO'
    ) NOT NULL DEFAULT 'EMPLEADO',

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    fechaRegistro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (idUsuario),

    UNIQUE KEY uk_usuario (
        usuario
    )

) ENGINE = InnoDB;


-- ============================================================
-- TABLA: empleados
-- ============================================================

CREATE TABLE empleados (

    idEmpleado INT NOT NULL AUTO_INCREMENT,

    idUsuario INT NULL,

    nombre VARCHAR(120) NOT NULL,

    fechaNacimiento DATE NULL,

    rfc VARCHAR(20) NULL,

    direccion VARCHAR(255) NULL,

    telefono VARCHAR(20) NULL,

    identificacion VARCHAR(100) NULL,

    fechaRegistro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (idEmpleado),

    UNIQUE KEY uk_empleado_usuario (
        idUsuario
    ),

    CONSTRAINT fk_empleado_usuario

        FOREIGN KEY (idUsuario)

        REFERENCES usuarios (
            idUsuario
        )

        ON UPDATE CASCADE

        ON DELETE SET NULL

) ENGINE = InnoDB;


-- ============================================================
-- TABLA: ubicaciones
-- ============================================================

CREATE TABLE ubicaciones (

    idUbicacion INT NOT NULL AUTO_INCREMENT,

    codigo VARCHAR(20) NOT NULL,

    pasillo VARCHAR(30) NOT NULL,

    estante VARCHAR(30) NOT NULL,

    nivel INT NOT NULL DEFAULT 1,

    descripcion VARCHAR(255) NULL,

    posicionX INT NOT NULL DEFAULT 0,

    posicionY INT NOT NULL DEFAULT 0,

    ancho INT NOT NULL DEFAULT 120,

    alto INT NOT NULL DEFAULT 160,

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (idUbicacion),

    UNIQUE KEY uk_ubicacion_codigo (
        codigo
    ),

    CONSTRAINT chk_ubicacion_nivel
        CHECK (
            nivel BETWEEN 1 AND 4
        ),

    CONSTRAINT chk_ubicacion_ancho
        CHECK (
            ancho > 0
        ),

    CONSTRAINT chk_ubicacion_alto
        CHECK (
            alto > 0
        )

) ENGINE = InnoDB;


-- ============================================================
-- TABLA: medicamentos
-- ============================================================

CREATE TABLE medicamentos (

    idMedicamento INT NOT NULL AUTO_INCREMENT,

    nombre VARCHAR(150) NOT NULL,

    presentacion VARCHAR(150) NULL,

    cantidad INT NOT NULL DEFAULT 0,

    codigoBarras VARCHAR(100) NULL,

    descripcion TEXT NULL,

    principioActivo VARCHAR(150) NULL,

    fabricante VARCHAR(150) NULL,

    contenido VARCHAR(100) NULL,

    precioCompra DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    precioVenta DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    stockMinimo INT NOT NULL DEFAULT 0,

    idUbicacion INT NULL,

    fechaRegistro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (idMedicamento),

    UNIQUE KEY uk_medicamento_codigo_barras (
        codigoBarras
    ),

    CONSTRAINT fk_medicamento_ubicacion

        FOREIGN KEY (
            idUbicacion
        )

        REFERENCES ubicaciones (
            idUbicacion
        )

        ON UPDATE CASCADE

        ON DELETE SET NULL,

    CONSTRAINT chk_medicamento_cantidad
        CHECK (
            cantidad >= 0
        ),

    CONSTRAINT chk_medicamento_stock_minimo
        CHECK (
            stockMinimo >= 0
        ),

    CONSTRAINT chk_medicamento_precio_compra
        CHECK (
            precioCompra >= 0
        ),

    CONSTRAINT chk_medicamento_precio_venta
        CHECK (
            precioVenta >= 0
        )

) ENGINE = InnoDB;


-- ============================================================
-- TABLA: ventas
-- ============================================================

CREATE TABLE ventas (

    idVenta INT NOT NULL AUTO_INCREMENT,

    idUsuario INT NOT NULL,

    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    metodoPago ENUM(
        'EFECTIVO',
        'TARJETA',
        'TRANSFERENCIA'
    ) NOT NULL,

    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    total DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    PRIMARY KEY (
        idVenta
    ),

    CONSTRAINT fk_venta_usuario

        FOREIGN KEY (
            idUsuario
        )

        REFERENCES usuarios (
            idUsuario
        )

        ON UPDATE CASCADE

        ON DELETE RESTRICT,

    CONSTRAINT chk_venta_subtotal
        CHECK (
            subtotal >= 0
        ),

    CONSTRAINT chk_venta_total
        CHECK (
            total >= 0
        )

) ENGINE = InnoDB;


-- ============================================================
-- TABLA: detalle_venta
-- ============================================================

CREATE TABLE detalle_venta (

    idDetalle INT NOT NULL AUTO_INCREMENT,

    idVenta INT NOT NULL,

    idMedicamento INT NOT NULL,

    cantidad INT NOT NULL,

    precioUnitario DECIMAL(10,2) NOT NULL,

    subtotal DECIMAL(12,2) NOT NULL,

    PRIMARY KEY (
        idDetalle
    ),

    CONSTRAINT fk_detalle_venta

        FOREIGN KEY (
            idVenta
        )

        REFERENCES ventas (
            idVenta
        )

        ON UPDATE CASCADE

        ON DELETE CASCADE,

    CONSTRAINT fk_detalle_medicamento

        FOREIGN KEY (
            idMedicamento
        )

        REFERENCES medicamentos (
            idMedicamento
        )

        ON UPDATE CASCADE

        ON DELETE RESTRICT,

    CONSTRAINT chk_detalle_cantidad
        CHECK (
            cantidad > 0
        ),

    CONSTRAINT chk_detalle_precio
        CHECK (
            precioUnitario >= 0
        ),

    CONSTRAINT chk_detalle_subtotal
        CHECK (
            subtotal >= 0
        )

) ENGINE = InnoDB;


-- ============================================================
-- TABLA: encuestas
-- ============================================================

CREATE TABLE encuestas (

    idEncuesta INT NOT NULL AUTO_INCREMENT,

    idVenta INT NULL,

    calificacion INT NOT NULL,

    comentario TEXT NULL,

    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        idEncuesta
    ),

    CONSTRAINT fk_encuesta_venta

        FOREIGN KEY (
            idVenta
        )

        REFERENCES ventas (
            idVenta
        )

        ON UPDATE CASCADE

        ON DELETE SET NULL,

    CONSTRAINT chk_encuesta_calificacion
        CHECK (
            calificacion BETWEEN 1 AND 5
        )

) ENGINE = InnoDB;


-- ============================================================
-- TABLA: movimientos_inventario
-- ============================================================

CREATE TABLE movimientos_inventario (

    idMovimiento INT NOT NULL AUTO_INCREMENT,

    idMedicamento INT NOT NULL,

    idUsuario INT NOT NULL,

    idVenta INT NULL,

    tipo ENUM(
        'ENTRADA',
        'VENTA',
        'AJUSTE',
        'DEVOLUCION'
    ) NOT NULL,

    cantidad INT NOT NULL,

    cantidadAnterior INT NOT NULL,

    cantidadNueva INT NOT NULL,

    descripcion VARCHAR(255) NULL,

    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        idMovimiento
    ),

    CONSTRAINT fk_movimiento_medicamento

        FOREIGN KEY (
            idMedicamento
        )

        REFERENCES medicamentos (
            idMedicamento
        )

        ON UPDATE CASCADE

        ON DELETE RESTRICT,

    CONSTRAINT fk_movimiento_usuario

        FOREIGN KEY (
            idUsuario
        )

        REFERENCES usuarios (
            idUsuario
        )

        ON UPDATE CASCADE

        ON DELETE RESTRICT,

    CONSTRAINT fk_movimiento_venta

        FOREIGN KEY (
            idVenta
        )

        REFERENCES ventas (
            idVenta
        )

        ON UPDATE CASCADE

        ON DELETE SET NULL,

    CONSTRAINT chk_movimiento_cantidad
        CHECK (
            cantidad >= 0
        ),

    CONSTRAINT chk_movimiento_anterior
        CHECK (
            cantidadAnterior >= 0
        ),

    CONSTRAINT chk_movimiento_nueva
        CHECK (
            cantidadNueva >= 0
        )

) ENGINE = InnoDB;


-- ============================================================
-- ÍNDICES
-- ============================================================


-- ------------------------------------------------------------
-- MEDICAMENTOS
-- ------------------------------------------------------------

CREATE INDEX idx_medicamento_nombre
ON medicamentos (
    nombre
);

CREATE INDEX idx_medicamento_principio
ON medicamentos (
    principioActivo
);

CREATE INDEX idx_medicamento_fabricante
ON medicamentos (
    fabricante
);

CREATE INDEX idx_medicamento_ubicacion
ON medicamentos (
    idUbicacion
);

CREATE INDEX idx_medicamento_activo
ON medicamentos (
    activo
);


-- ------------------------------------------------------------
-- VENTAS
-- ------------------------------------------------------------

CREATE INDEX idx_venta_usuario
ON ventas (
    idUsuario
);

CREATE INDEX idx_venta_fecha
ON ventas (
    fecha
);


-- ------------------------------------------------------------
-- DETALLE VENTA
-- ------------------------------------------------------------

CREATE INDEX idx_detalle_medicamento
ON detalle_venta (
    idMedicamento
);


-- ------------------------------------------------------------
-- MOVIMIENTOS
-- ------------------------------------------------------------

CREATE INDEX idx_movimiento_medicamento
ON movimientos_inventario (
    idMedicamento
);

CREATE INDEX idx_movimiento_usuario
ON movimientos_inventario (
    idUsuario
);

CREATE INDEX idx_movimiento_fecha
ON movimientos_inventario (
    fecha
);

CREATE INDEX idx_movimiento_tipo
ON movimientos_inventario (
    tipo
);


-- ============================================================
-- DATOS DE PRUEBA
-- ============================================================


-- ============================================================
-- USUARIO ADMINISTRADOR
-- ============================================================
--
-- IMPORTANTE:
-- La contraseña está en texto plano solamente porque el
-- proyecto todavía está en etapa de desarrollo.
--
-- Usuario: admin
-- Contraseña: admin123
--
-- Posteriormente se utilizará bcrypt.
-- ============================================================

INSERT INTO usuarios (
    nombre,
    usuario,
    contrasena,
    rol,
    activo
)
VALUES (
    'Administrador',
    'admin',
    'admin123',
    'ADMIN',
    TRUE
);


-- ============================================================
-- EMPLEADO ADMINISTRADOR
-- ============================================================

INSERT INTO empleados (
    idUsuario,
    nombre,
    fechaNacimiento,
    rfc,
    direccion,
    telefono,
    identificacion,
    activo
)
VALUES (
    1,
    'Administrador',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    TRUE
);


-- ============================================================
-- UBICACIONES DE PRUEBA
--
-- 4 niveles por estante.
--
-- posicionX y posicionY son utilizados por mapa.py.
-- mapa.py agrega separación visual adicional.
-- ============================================================

INSERT INTO ubicaciones (
    codigo,
    pasillo,
    estante,
    nivel,
    descripcion,
    posicionX,
    posicionY,
    ancho,
    alto,
    activo
)
VALUES

(
    'A1',
    'A',
    '1',
    1,
    'Estante A1',
    100,
    100,
    120,
    160,
    TRUE
),

(
    'A2',
    'A',
    '2',
    2,
    'Estante A2',
    250,
    100,
    120,
    160,
    TRUE
),

(
    'A3',
    'A',
    '3',
    3,
    'Estante A3',
    400,
    100,
    120,
    160,
    TRUE
),

(
    'A4',
    'A',
    '4',
    4,
    'Estante A4',
    550,
    100,
    120,
    160,
    TRUE
),

(
    'B1',
    'B',
    '1',
    1,
    'Estante B1',
    100,
    300,
    120,
    160,
    TRUE
),

(
    'B2',
    'B',
    '2',
    2,
    'Estante B2',
    250,
    300,
    120,
    160,
    TRUE
),

(
    'B3',
    'B',
    '3',
    3,
    'Estante B3',
    400,
    300,
    120,
    160,
    TRUE
),

(
    'B4',
    'B',
    '4',
    4,
    'Estante B4',
    550,
    300,
    120,
    160,
    TRUE
);



INSERT INTO medicamentos (
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
    activo
)
VALUES

(
    'Paracetamol',
    'Caja con 20 tabletas',
    30,
    '750000000001',
    'Analgésico y antipirético',
    'Paracetamol',
    'Genérico',
    '500 mg',
    25.00,
    40.00,
    10,
    1,
    TRUE
),

(
    'Ibuprofeno',
    'Caja con 20 tabletas',
    20,
    '750000000002',
    'Analgésico y antiinflamatorio',
    'Ibuprofeno',
    'Genérico',
    '400 mg',
    30.00,
    50.00,
    8,
    2,
    TRUE
),

(
    'Amoxicilina',
    'Caja con 12 cápsulas',
    15,
    '750000000003',
    'Antibiótico',
    'Amoxicilina',
    'Genérico',
    '500 mg',
    55.00,
    85.00,
    5,
    3,
    TRUE
),

(
    'Loratadina',
    'Caja con 10 tabletas',
    25,
    '750000000004',
    'Antihistamínico',
    'Loratadina',
    'Genérico',
    '10 mg',
    20.00,
    35.00,
    7,
    4,
    TRUE
);




CREATE VIEW vista_medicamentos_ubicacion AS

SELECT

    m.idMedicamento,

    m.nombre,

    m.presentacion,

    m.cantidad,

    m.codigoBarras,

    m.principioActivo,

    m.fabricante,

    m.contenido,

    m.precioCompra,

    m.precioVenta,

    m.stockMinimo,

    m.activo,

    u.idUbicacion,

    u.codigo AS codigoUbicacion,

    u.pasillo,

    u.estante,

    u.nivel,

    u.descripcion AS descripcionUbicacion

FROM medicamentos AS m

LEFT JOIN ubicaciones AS u

    ON m.idUbicacion = u.idUbicacion;


-- ============================================================
-- VISTA: stock bajo
-- ============================================================

CREATE VIEW vista_stock_bajo AS

SELECT

    m.idMedicamento,

    m.nombre,

    m.presentacion,

    m.cantidad,

    m.stockMinimo,

    m.codigoBarras,

    m.principioActivo,

    m.fabricante,

    u.codigo AS ubicacion,

    u.pasillo,

    u.estante,

    u.nivel

FROM medicamentos AS m

LEFT JOIN ubicaciones AS u

    ON m.idUbicacion = u.idUbicacion

WHERE

    m.activo = TRUE

    AND m.cantidad <= m.stockMinimo;



CREATE VIEW vista_ventas_por_usuario AS

SELECT

    u.idUsuario,

    u.nombre AS nombreUsuario,

    u.usuario,

    COUNT(v.idVenta) AS numeroVentas,

    COALESCE(
        SUM(v.total),
        0
    ) AS totalVendido,

    COALESCE(
        AVG(v.total),
        0
    ) AS ticketPromedio

FROM usuarios AS u

LEFT JOIN ventas AS v

    ON u.idUsuario = v.idUsuario

GROUP BY

    u.idUsuario,

    u.nombre,

    u.usuario;


