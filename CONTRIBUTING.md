# Contribuir a Mistik Launcher

¡Gracias por tu interés en contribuir a **Mistik Launcher**! 🎉

Este documento explica cómo puedes participar en el proyecto de forma efectiva y respetuosa.

## Tabla de contenidos

- [Cómo reportar un problema](#cómo-reportar-un-problema)
- [Cómo proponer un cambio](#cómo-proponer-un-cambio)
- [Configuración del entorno de desarrollo](#configuración-del-entorno-de-desarrollo)
- [Flujo de trabajo de ramas](#flujo-de-trabajo-de-ramas)
- [Estilo de código](#estilo-de-código)

## Cómo reportar un problema

Antes de abrir un issue nuevo:

1. Revisa los [issues existentes](https://github.com/jesujaque/mistik-launcher/issues) para evitar duplicados.
2. Verifica la documentación (`README.md`) y este archivo.

Si el problema no está reportado, abre un nuevo issue con:

- Un título claro y descriptivo.
- Pasos para reproducir el problema.
- Comportamiento esperado vs. comportamiento real.
- Tu sistema operativo y versión.
- Capturas de pantalla o logs si es posible.

## Cómo proponer un cambio

1. Abre un issue describiendo la mejora o el bug antes de empezar a codificar.
2. Espera a que se valide la idea antes de invertir tiempo en una implementación grande.
3. Sigue el flujo de ramas descrito más abajo.
4. Abre un pull request con una descripción clara de los cambios.

## Configuración del entorno de desarrollo

1. Haz fork del repositorio y clona tu fork.
2. Crea una rama descriptiva:

   ```bash
   git checkout -b feat/nombre-de-la-mejora
   ```

3. Instala las dependencias necesarias:

   ```bash
   pip install customtkinter requests py7zr pillow
   ```

4. Ejecuta el lanzador:

   ```bash
   python mistik-launcher-code.py
   ```

5. Compila el ejecutable si vas a probar la versión empaquetada:

   ```bash
   python -m PyInstaller --noconfirm --onefile --windowed --name "MistikLauncher" --icon "assets/icon.ico" --add-data "assets;assets" --collect-all customtkinter mistik-launcher-code.py
   ```

## Flujo de trabajo de ramas

- La rama por defecto del proyecto es `develop`.
- Las ramas de funcionalidades deben empezar con `feat/`.
- Las ramas de corrección de bugs deben empezar con `fix/`.
- Los cambios de documentación pueden ir en `docs/`.

## Estilo de código

- Usa Python con estilo **PEP 8** cuando sea posible.
- Nombra variables y funciones en `snake_case`.
- Comenta el código cuando sea necesario para explicar lógica compleja.
- No mezcles cambios de funcionalidad con cambios de estilo o refactorización grandes.
- Actualiza el `README.md` si tu cambio afecta la forma en la que se usa o se instala el proyecto.

## Licencia

Al contribuir a **Mistik Launcher**, aceptas que tus contribuciones se licencian bajo la [MIT License](LICENSE).

## Preguntas

Si tienes dudas sobre cómo proceder, abre un issue y pregunta. ¡Estamos aquí para ayudarte!
