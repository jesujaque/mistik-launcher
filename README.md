# Mistik Launcher

[![CI](https://github.com/jesujaque/mistik-launcher/actions/workflows/ci.yml/badge.svg)](https://github.com/jesujaque/mistik-launcher/actions/workflows/ci.yml)
[![Update Emulator Links](https://github.com/jesujaque/mistik-launcher/actions/workflows/update-emulator-links.yml/badge.svg)](https://github.com/jesujaque/mistik-launcher/actions/workflows/update-emulator-links.yml)

**Mistik Launcher** es un launcher de emuladores de videojuegos que centraliza en una única interfaz gráfica el download, la instalación y la ejecución de los emuladores más populares, de forma automática y portable.

## Sobre el proyecto

**Mistik Launcher** es un proyecto de software que busca reunir los emuladores de los videojuegos más populares en un mismo launcher.

El objetivo del proyecto es simple y ambicioso: en lugar de tener que descargar, descomprimir y configurar cada emulador por separado, **Mistik Launcher** centraliza todo en una única interfaz gráfica que se encarga de gestionar los ejecutables, los directorios y las actualizaciones de los mismos.

Con Mistik Launcher, el usuario solo tiene que preocuparse por jugar: el launcher descarga el emulador que necesites, lo extrae en la carpeta correcta, le muestra el estado (instalado / no instalado) y le permite ejecutarlo con un simple clic.

## Características

- **Interfaz moderna y oscura**: desarrollada con Python y CustomTkinter, con un diseño cuidado y colores propios del proyecto (naranja vibrante y verdes de acción).
- **Arquitectura portátil**: el proyecto se distribuye como un único archivo ejecutable (`MistikLauncher.exe`) compilado con PyInstaller (`--onefile --windowed`), lo que permite llevarlo en cualquier carpeta (por ejemplo, una carpeta de juegos) sin necesidad de instalar nada más en el sistema.
- **Gestión automática de emuladores**: cada emulador tiene su propia tarjeta en la interfaz, con su consola, su emulador y su estado.
- **Descarga e instalación automática**: los emuladores se descargan directamente desde sus repositorios oficiales (GitHub Releases, sitios de releases, etc.) y se gestiona el formato de descarga (`.7z`, `.zip` o instalador `.exe`).
- **Barra de progreso**: durante la descarga se muestra una barra de progreso en tiempo real.
- **Acciones dinámicas**: el botón de cada tarjeta cambia dinámicamente según el estado:
  - *Descargar e Instalar* (verde): si el emulador aún no está instalado.
  - *EJECUTAR* (naranja): si el emulador está instalado y listo para jugar.
  - *DESINSTALAR*: para eliminar por completo la carpeta del emulador.
- **Manejo de errores**: si algo falla durante la descarga o la instalación, el estado de la tarjeta se pone en rojo para que el usuario sepa que hay que reintentar.

## Emuladores soportados

Actualmente el launcher incluye tarjetas para los siguientes emuladores:

| Consola | Emulador | Estado |
|---|---|---|
| Wii | Dolphin | ✅ Descargable e instalable |
| Wii U | Cemu | ✅ Descargable e instalable |
| Nintendo 3DS | Azahar | ✅ Descargable e instalable |
| PlayStation 1 | DuckStation | 🚧 En desarrollo |
| PlayStation 2 | PCSX2 | 🚧 En desarrollo |
| PSP | PPSSPP | 🚧 En desarrollo |

## Cómo adquirir y usar el launcher

El archivo ejecutable `MistikLauncher.exe` no se versiona directamente dentro del repositorio para mantener el historial ligero y seguro.

Puedes adquirirlo de dos formas:

### Opción A: Descargar desde GitHub Releases (Recomendado)
1. Ve a la sección de [Releases de este repositorio](https://github.com/jesujaque/mistik-launcher/releases).
2. Descarga el archivo `MistikLauncher.exe` de la última versión publicada.
3. Colócalo en la carpeta donde quieras tener tus emuladores.

### Opción B: Compilarlo tú mismo desde el código fuente
Si prefieres generar el ejecutable por tu cuenta:
1. Clona el repositorio e instala las dependencias:
   ```bash
   pip install customtkinter requests py7zr pillow pyinstaller
   ```
2. Compílalo ejecutando:
   ```bash
   python -m PyInstaller --noconfirm --onefile --windowed --name "MistikLauncher" --icon "assets/icon.ico" --add-data "assets;assets" --collect-all customtkinter mistik-launcher-code.py
   ```
3. El archivo `MistikLauncher.exe` generado se encontrará en la carpeta `dist/`.

---

## Cómo usar el launcher:

1. Ejecuta `MistikLauncher.exe` en la carpeta donde quieras almacenar y gestionar los emuladores.
2. Descarga los emuladores que necesites con el botón **"Descargar e Instalar"**.
3. Una vez completada la descarga y extracción automática, pulsa **"EJECUTAR"** para abrir el emulador.
4. ¡Disfruta jugando!
5. Si no sabes cómo configurar o funciona algún emulador, se recomienda buscar un tutorial o video explicativo en YouTube.

> [!NOTE]
> Cabe destacar que el proyecto **no incluye ni distribuye juegos ni BIOS** (NO JUEGOS, NO BIOS). Cada usuario debe proveer sus propios archivos por medios legales.

## ¿Cómo funciona?

### Descarga e instalación

Cuando el usuario pulsa el botón de una tarjeta que no tiene el ejecutable instalado:

1. El launcher detecta la URL de descarga configurada para ese emulador.
2. Detecta el tipo de archivo de la descarga (`.exe`, `.zip` o `.7z`).
3. Si es un instalador (`.exe`), lo descarga y lo ejecuta para instalar el emulador.
4. Si es un archivo comprimido (`.zip` o `.7z`), lo descarga y lo extrae en la carpeta correspondiente del emulador.
5. Muestra el progreso de la descarga mediante una barra de progreso.
6. Una vez finalizada la operación, el estado de la tarjeta se actualiza automáticamente y el botón pasa a la opción de *EJECUTAR*.

### Ejecución

Cuando el usuario pulsa el botón **EJECUTAR**, el launcher localiza el ejecutable del emulador y lo lanza con el directorio de trabajo correspondiente, de forma que el emulador encuentre sus dependencias y archivos correctamente.

### Desinstalación

El usuario puede desinstalar un emulador con el botón **DESINSTALAR**, lo que elimina la carpeta completa asociada al emulador, dejando el estado de la tarjeta como "no instalado" otra vez.

## Edición AC (experimental) ⚠️

El archivo **`mistik-launcher-code-AC-EDITION.py`** es una **prueba experimental** que **no forma parte de la versión oficial** del launcher.

Su objetivo era añadir un sistema de **sincronización automática de partidas** para el emulador de Nintendo 3DS (Animal Crossing), pero **actualmente no funciona** y **no se está manteniendo, probando ni teniendo en cuenta** en el desarrollo.

- Las pruebas (CI) y la actualización automática de enlaces **ignoran este archivo**.
- Por ahora el proyecto se centra únicamente en el código oficial (`mistik-launcher-code.py`).
- Más adelante se retomará esta idea y, si funciona, se implementará directamente en el archivo oficial.

## Cómo ejecutar desde el código fuente (desarrollo)

Si quieres ejecutar Mistik Launcher directamente desde el código Python:

1. Clona el repositorio.
2. Instala las dependencias necesarias:

```bash
pip install customtkinter requests py7zr pillow
```

3. Ejecuta el lanzador:

```bash
python mistik-launcher-code.py
```

### Compilar el ejecutable (PyInstaller)

Para generar el archivo `MistikLauncher.exe` a partir del código fuente:

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "MistikLauncher" --icon "assets/icon.ico" --add-data "assets;assets" --collect-all customtkinter mistik-launcher-code.py
```

## Estructura del proyecto

```
mistik-launcher/
├── mistik-launcher-code.py        # Código fuente oficial
├── mistik-launcher-code-AC-EDITION.py  # Experimental (no soportado por ahora)
├── assets/                         # Imágenes de consolas y recursos
├── config/                         # Configuraciones y recursos auxiliares
├── CODE_OF_CONDUCT.md              # Código de conducta
├── CONTRIBUTING.md                 # Guía de contribución
├── LICENSE                         # Licencia MIT
├── SECURITY.md                     # Política de seguridad
└── README.md
```

## Actualización automática de enlaces de descarga

El repositorio incluye un **workflow de GitHub Actions** (`update-emulator-links`) que mantiene automáticamente los enlaces de descarga de los emuladores actualizados.

- El workflow se ejecuta de forma **automática** (programada semanalmente) o de forma **manual** (mediante `workflow_dispatch`).
- Cuando un emulador publica una nueva release, el workflow consulta la última versión disponible y actualiza el enlace en el archivo fuente oficial (`mistik-launcher-code.py`).
- Si detecta cambios, crea la rama `automation/emulator-links`, hace un commit con el mensaje `ci: actualizar enlaces de descarga de emuladores a la última release` y abre un **Pull Request** contra `develop`.
- El PR ejecuta CI sobre la rama y **solo se puede mergear cuando el check `validate` está en verde**.

Con esto, cuando los usuarios descarguen una nueva versión del ejecutable `MistikLauncher.exe`, el launcher ya tendrá los enlaces actualizados a las últimas releases de los emuladores.

> Emuladores con enlaces configurados actualmente: **Dolphin**, **Cemu** y **Azahar**.

## Notas importantes

- El launcher no incluye juegos ni BIOS, ya que no se pueden distribuir de forma gratuita. Los usuarios deben obtener los juegos por sus canales oficiales.
- Los emuladores se descargan a las carpetas indicadas dentro de la propia carpeta del proyecto (por ejemplo, `emulators/Dolphin`).
- Si no sabes cómo funciona el emulador que deseas, se recomienda buscar un video en YouTube que lo explique.

## Contribuir

Si quieres contribuir al proyecto, por favor lee nuestro [código de conducta](CODE_OF_CONDUCT.md) y nuestra [guía de contribución](CONTRIBUTING.md).

Si descubres una vulnerabilidad de seguridad, consulta nuestra [política de seguridad](SECURITY.md).

## Créditos

- **Mistik Launcher** - Creado por [jesujaque](https://github.com/jesujaque)
- Desarrollado con **Python**, **CustomTkinter**, **requests**, **py7zr** y **Pillow**.
- Las marcas y nombres de los emuladores pertenecen a sus respectivos propietarios.
