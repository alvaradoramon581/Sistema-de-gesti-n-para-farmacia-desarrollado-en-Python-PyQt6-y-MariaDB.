# Proyecto Farmacia

Sistema de escritorio para la gestión de una farmacia y la localización visual de medicamentos mediante un mapa de estantes.

Desarrollado con Python, PyQt6 y MariaDB.

## Descripción

El sistema permite administrar medicamentos, inventario y usuarios, además de localizar visualmente la posición de un medicamento dentro de la farmacia.

Una de sus principales características es el mapa interactivo de estantes, donde se puede identificar el estante y nivel correspondiente de un medicamento.

## Funciones implementadas

- Inicio de sesión.
- Control de usuarios por rol.
- Gestión de medicamentos.
- Registro de medicamentos.
- Modificación de medicamentos.
- Desactivación y reactivación de medicamentos.
- Control de inventario.
- Registro de entradas.
- Registro de ajustes.
- Registro de devoluciones.
- Historial de movimientos de inventario.
- Búsqueda de medicamentos.
- Búsqueda por nombre.
- Búsqueda por código de barras.
- Búsqueda por principio activo.
- Búsqueda por fabricante.
- Mapa visual de la farmacia.
- Localización por estante.
- Localización por nivel.
- Estantes de cuatro niveles.
- Resaltado visual del nivel donde se encuentra el medicamento.
- Registro y consulta de ventas.
- Gestión de empleados y cuentas de acceso.
- Captura de lote y fecha de caducidad en la ficha de Medicamentos.
- Alertas de existencias bajas, próxima caducidad y fechas pendientes.
- Encuestas de satisfacción.
- Reportes de ventas, ventas por usuario, inventario y empleados con exportación CSV.

## Funciones pendientes

- Migración de las contraseñas antiguas (las cuentas creadas o actualizadas desde Empleados ya usan bcrypt).

## Tecnologías utilizadas

- Python
- PyQt6
- MariaDB
- MySQL Workbench
- mysql-connector-python
- bcrypt

## Requisitos

Se recomienda utilizar:

- Python 3.11 o superior
- MariaDB
- MySQL Workbench
- pip

## Instalación

Para clonar el proyecto y preparar Python en Windows, ejecuta lo siguiente en PowerShell.

```powershell
git clone https://github.com/alvaradoramon581/Sistema-de-gesti-n-para-farmacia-desarrollado-en-Python-PyQt6-y-MariaDB..git farmacia
cd farmacia
py -m pip install -r requirements.txt
Copy-Item config.example.py config.py
```

Edita `config.py` con los datos de conexión de MariaDB. En una instalación nueva, importa primero `database/farmacia_local.sql` en MariaDB. Si ya tienes una base con registros, omite esa importación y ejecuta directamente la migración.

```powershell
py -B migrar.py
py -B login.py
```

El instalador prepara las tablas de encuestas y agrega los campos de lote y caducidad a Medicamentos.
