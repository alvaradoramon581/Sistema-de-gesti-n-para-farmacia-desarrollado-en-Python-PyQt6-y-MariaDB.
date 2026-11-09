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

## Cómo colaborar

Usamos **trunk-based development**. La rama `main` concentra la versión integrada de la farmacia. Cada tarea se prepara en una rama de corta duración y se integra mediante un *pull request* (PR).

1. Actualiza tu copia con `git switch main` y `git pull --ff-only`.
2. Crea una rama para un cambio concreto, por ejemplo `git switch -c fix/consulta-empleados`.
3. Guarda el cambio en commits pequeños y publica la rama con `git push -u origin HEAD`.
4. Abre un PR hacia `main`, explica qué cambió y revisa los resultados de CI. Si falla alguna comprobación, corrige el problema en la misma rama. Integra el PR cuando las comprobaciones pasen y elimina la rama de la tarea.

### Convención de commits

Escribe el asunto como `tipo(ámbito): resumen`. El ámbito es opcional e identifica el módulo afectado. Usa un resumen breve en español que describa el cambio. Algunos ejemplos son `fix(empleados): corrige la consulta por nombre`, `test(ventas): comprueba dos ventas simultáneas` y `ci: valida el proyecto con MariaDB`.

Usa `feat` para una función, `fix` para una corrección, `test` para pruebas, `docs` para documentación y `ci` para integración continua. También se aceptan `build`, `chore`, `perf`, `refactor`, `revert` y `style`. Puedes añadir `!` antes de los dos puntos para indicar un cambio incompatible. La verificación se aplica a los asuntos de commits nuevos de la tarea y omite los commits de fusión.

### Integración continua

GitHub Actions comprueba cada PR hacia `main` y cada actualización de `main`. En la pestaña **Checks** del PR puedes abrir los resultados de cada tarea.

| Comprobación | Qué verifica |
| --- | --- |
| Convención de commits | Cada asunto nuevo sigue el formato del equipo. |
| Compilación | Python 3.11 compila los archivos `.py` versionados y avisa si encuentra errores de sintaxis. |
| Análisis estático | Ruff analiza el código y las pruebas para detectar, entre otros defectos, nombres sin definir e importaciones sin usar. Las dos excepciones heredadas para estilos del login están en `ruff.toml`. |
| Pruebas con MariaDB | La suite ejecuta operaciones con datos ficticios en bases temporales de MariaDB 11.4 y acciona controles PyQt6 en modo `offscreen`. El trabajo falla si hay errores, si se omiten pruebas o si no se descubre ninguna. |

Para reproducir las comprobaciones en PowerShell desde la raíz del repositorio, instala las dependencias de la aplicación y usa una instancia de MariaDB de desarrollo en `config.py`. La cuenta de pruebas necesita permiso para crear y eliminar sus bases temporales. Con `FARMACIA_ESQUEMA_ARCHIVO=1` la estructura inicial se lee del SQL versionado.

```powershell
py -m pip install -r requirements-dev.txt
py scripts/verificar_commits.py origin/main HEAD
py -m py_compile (git ls-files '*.py')
py -m ruff check .
$env:QT_QPA_PLATFORM = "offscreen"
$env:FARMACIA_PRUEBAS_DB = "1"
$env:FARMACIA_ESQUEMA_ARCHIVO = "1"
py -B -m unittest discover -s tests -v
```
