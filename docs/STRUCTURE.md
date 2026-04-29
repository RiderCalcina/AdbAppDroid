# Estructura del Proyecto

AdbAppDroid v5.0 utiliza una arquitectura modular diseñada para la gestión multi-dispositivo simultánea. A continuación se describe el propósito de cada directorio y archivo clave.

## 📂 Directorio Raíz

- `main.py`: El punto de entrada principal de la aplicación. Inicializa la ventana y el bucle de eventos.
- `README.md` / `requirements.txt`: Documentación principal e información de dependencias.
- `history.json`: Archivo de caché de IPs conectadas recientemente.
- `assets/`: Contiene recursos multimedia de la aplicación, como el `icon.ico`.
- `docs/`: Carpeta que contiene toda la documentación técnica detallada (Manuales, Changelog, Arquitectura, y apuntes como `Implementación.txt`).
- `cache/`: (Generado) Almacena datos temporales como los iconos de las aplicaciones extraídos (`cache/icons/`) y logs de la aplicación.
- `platform-tools/`: (Generado/Descargado) Contiene los binarios de Android Debug Bridge (`adb.exe`).
- `scrcpy/`: (Generado/Descargado) Herramienta para control de pantalla y grabación.
- `manual/`: Recursos e imágenes para el manual del usuario web.

---

## 📦 Paquete `adbappkiller/`

Este es el núcleo del proyecto, dividido en subpaquetes lógicos.

### 🔌 `core/` (Lógica de Negocio)
- `adb_controller.py`: Contiene la clase `ADBController`. Gestiona comandos ADB mediante inyección de `serial` para soporte multi-dispositivo. Incluye una cola secuencial de iconos y lógica dinámica de monitoreo de CPU.
- `downloader.py`: Clase `Downloader`. Gestiona la descarga y extracción de herramientas externas.

### 🎨 `ui/` (Interfaz de Usuario)
- `main_window.py`: Clase `MainWindow`. Define la interfaz principal con selector de dispositivo activo (`CTkOptionMenu`) y gestión de múltiples procesos de Scrcpy.
- `components.py`: Contiene componentes reutilizables como `AppInfoWidget`, `CPUGraphWidget`, `RSSMarqueeWidget` (con cargador redundante), y el cuadro de diálogo nativo `CTkWarningDialog`.


### 🛠 `utils/` (Utilidades)
- `config.py`: Definiciones de configuración global, paletas de colores (temas), rutas constantes y strings de texto.
- `helpers.py`: Funciones puras de utilidad (limpieza de strings, validación de nombres de paquetes, etc.) que no dependen de la UI ni de ADB.

---

## 🔄 Flujo de Datos

1. `main.py` instancia `MainWindow`.
2. `MainWindow` crea una instancia de `ADBController`.
3. Un hilo secundario en `MainWindow` llama a `ADBController` periódicamente para obtener la app en primer plano.
4. Si faltan herramientas, `MainWindow` usa `Downloader` para instalarlas sin bloquear la interfaz.
5. Los eventos de la UI (clashes en botones) disparan métodos en `MainWindow` que ejecutan comandos a través de `ADBController`.

---

> [!TIP]
> Si deseas extender la funcionalidad, añade los nuevos comandos ADB en `adb_controller.py` y luego crea el botón correspondiente en `main_window.py`.
