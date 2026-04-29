# Control de Cambios (Changelog)

Historial de versiones y mejoras de **AdbAppDroid**.

## [v5.0] - 2026-04-29
### ✨ Novedades (Multi-Device Era)
- **Gestión Multi-Dispositivo**: Implementación de soporte para múltiples dispositivos conectados simultáneamente vía USB o WiFi.
- **Selector de Dispositivo Activo**: Nuevo menú desplegable (`CTkOptionMenu`) en la cabecera para alternar el control entre dispositivos.
- **Espejos Simultáneos**: Posibilidad de abrir múltiples ventanas de Scrcpy al mismo tiempo para diferentes dispositivos.
- **Grabación Independiente**: Sistema de procesos basado en diccionarios que permite grabar un dispositivo específico sin afectar la visualización de otros.

### 🔧 Mejoras Técnicas
- **Refactorización de ADBController**: Inyección obligatoria de `serial` en todos los métodos de gestión de apps y extracción de iconos.
- **Optimización de Monitoreo**: Lógica de `device_monitor` mejorada para sincronizar el estado de la UI con la lista dinámica de dispositivos.
- **Aislamiento de Procesos**: Uso de diccionarios de procesos para evitar colisiones entre sesiones de espejo/grabación.

## [v4.4] - 2026-03-04
### ✨ Novedades
- **Métricas CPU Normalizadas**: Implementación de visualización 0-100% basada en la resta del tiempo "Idle" del kernel, compatible con SoCs multi-núcleo modernos.
- **Gráfico de Rendimiento en Vivo**: Nuevo widget de gráfica tipo scroll con rejilla de referencia.
- **Marquesina RSS Dinámica**: Integración del feed en el panel derecho con diseño compacto, clicleable y estilizado.
- **Cargador RSS de Emergencia**: Fallback automático a `urllib` para garantizar noticias incluso con errores de certificados SSL/versionado de librerías.
- **Panel Izquierdo Full-Height**: Extensión del área de logs para aprovechar todo el espacio vertical disponible.

### 🔧 Mejoras Técnicas
- **Parseo de Procesos Blindado**: Soporte para formatos variables de `top` (ej. cabeceras tipo `S[%CPU]`).
- **Limpieza de UI**: Ajustes de bordes y márgenes (`border_width=1`, `corner_radius=8`) en nuevos módulos.

## [v4.3] - 2026-02-25
### ✨ Novedades
- **Reconocimiento Dinámico de CPU**: Se eliminó la dependencia de un diccionario estático de mapeo (`CHIPSET_MAP`) para la identificación de procesadores.
- **Identidad Universal**: El sistema ahora lee directamente el modelo SoC (`ro.soc.model`), la plataforma base (`ro.board.platform`) o el hardware (`ro.hardware`) del dispositivo. Esto permite identificar automáticamente procesadores de ultimísima generación (como el Snapdragon 8 Elite) sin requerir actualizaciones de la aplicación.
- **Respaldo de Identificación**: Se implementó una lectura directa de `/proc/cpuinfo` como método de respaldo extremo para garantizar que la interfaz siempre muestre información relevante en lugar de mensajes genéricos como "DESCONOCIDA".

## [v4.2] - 2026-02-24
- **Unificación de Versión**: Se ha estandarizado la versión del proyecto a v4.2 en toda la documentación, código y manuales HTML.
- **Renombramiento Estructural**: El script principal `main_v32.py` ha sido permanentemente renombrado a `main.py` para mayor claridad y mantenibilidad a largo plazo.

## [v3.6] - 2026-02-22
### ✨ Novedades
- **Mirroring de Audio de Alta Fidelidad**: Implementación de streaming en formato **Raw PCM** para el espejo (Scrcpy), solucionando errores críticos de drivers de audio (WASAPI) en Windows.
- **Audio Continuo en Grabación**: Optimización de parámetros para permitir que el audio siga sonando en los altavoces del PC mientras se realiza una grabación de video.
- **Conexión Blindada**: Inclusión forzada del argumento `--serial` en todas las ejecuciones de Scrcpy, eliminando fallos de inicio cuando hay múltiples dispositivos conectados (USB/WiFi).
- **Sistema de Diagnóstico**: Captura automática de logs de Scrcpy en `cache/scrcpy_error.log`, permitiendo identificar problemas de conexión sin necesidad de consola.

### 🔧 Mejoras Técnicas
- Centralización de la lógica de espejo en `ADBController`.
- Ajuste de buffers de audio a 100ms para mayor estabilidad.
- Reparación de `NameError` en el hilo de lanzamiento de espejo.

## [v3.5] - 2026-02-19
### ✨ Novedades
- **Renombramiento Oficial**: La aplicación ha pasado de llamarse *ADBAppKiller* a **AdbAppDroid**, obteniendo una nueva identidad.
- **Icono Propio**: Se ha implementado la carga de un icono de ventana personalizado (`assets/icon.ico`).
- **Advertencias Nativas Integradas**: Se ha reemplazado el sistema de advertencias del sistema operativo por un cuadro de diálogo nativo de tema oscuro (`CTkWarningDialog`), el cual adopta el icono de la ventana principal y los colores rojizos de peligro para una experiencia visual más unificada.
- **Advertencias Críticas de Seguridad**: Estos nuevos diálogos actúan como confirmaciones severas al intentar **Desinstalar** o **Desactivar** aplicaciones identificadas como del sistema, previniendo daños accidentales al dispositivo (bootloops).
- **Lectura Optimizada**: Se eliminaron las etiquetas redundantes de estado inferior de la ventana, permitiendo la expansión dinámica del panel de registro (App Info), mostrando más datos de permisos sin necesidad de desplazamiento.
- **Mejoras en RSS**: El título del panel de noticias ahora incluye un enlace directo y enlazable a la web del desarrollador (QwertyAserty.com).

### 🧹 Mantenimiento y Estructura
- **Limpieza Profunda**: Eliminados archivos obsoletos, copias de seguridad (`.zip`), scripts antiguos (`adbappkiller-v31.py`), carpetas vacías y logs viejos.
- **Reorganización de Directorios**:
  - Creada carpeta `assets/` para recursos multimedia (iconos).
  - Movidos documentos técnicos sueltos (`Adbutils.md`, `Implementación.txt`) a la carpeta `docs/` para mantener la raíz limpia exclusivamente para ejecución y configuración (`main_v32.py`, `README.md`, `requirements.txt`, `history.json`).

## [v3.4] - 2026-02-05
### ✨ Novedades
- **Panel de Conexiones Estilizado**: Reorganización con títulos en **verde tecnológico (#00FF99)** y diseño minimalista.
- **USB Tethering (Android 📱→💻 PC)**: Nueva función para compartir internet del celular a la PC.
- **Botón de Estado Dinámico**: El botón de Tethering ahora tiene tamaño estándar y cambia a rojo (**Desactivar**) cuando está activo, eliminando indicadores externos innecesarios.
- **Compatibilidad con Samsung**: Corregido el error `opId:1`, permitiendo que el Tethering funcione sin problemas en dispositivos Samsung modernos.
- **Optimización de Visibilidad**: Altura de ventana incrementada a **720px** para garantizar que el Feed RSS sea siempre visible.
- **Tooltips Informativos**: Descripciones emergentes en todos los controles de conexión.

### 🔧 Mejoras Técnicas
- Agregados métodos en `ADBController`: `enable_usb_tethering`, `disable_usb_tethering`, `get_tethering_status`
- Reorganización de la UI usando `pack()` para mejor gestión de espacio
- Reducción de padding y tamaños de controles (26-28px de altura)
- Eliminación de funcionalidades no esenciales para simplificar la interfaz

## [v3.3.1] - 2026-02-05 (Hotfix)
### 🐛 Correcciones
- **Inicialización Automática del Servidor ADB**: Se agregó el método `_ensure_adb_server()` en `ADBController` que inicia automáticamente el servidor ADB al instanciar el controlador.
  - **Problema resuelto**: Errores `WinError 10061` y `WinError 10054` al intentar listar dispositivos con `adbutils` cuando el servidor ADB no estaba ejecutándose.
  - **Implementación**: El servidor se inicia de forma silenciosa (sin ventanas emergentes) durante la inicialización del controlador.
  - **Beneficios**: La aplicación ahora funciona correctamente desde el primer arranque sin requerir intervención manual del usuario.

## [v3.3] - 2024-02-04
### ✨ Novedades
- **Rediseño Interfaz Horizontal**: Nueva disposición apaisada (Horizontal) que separa el panel de Log (Izquierda) de los controles (Derecha) para un flujo de trabajo más natural.
- **Posicionamiento Automático**: La ventana se sitúa automáticamente en el lado izquierdo de la pantalla con un margen de cortesía al iniciarse.
- **Encabezado de Equipo Expandido**: Visualización detallada en tiempo real de Marca, Modelo, RAM, CPU, Resolución, Batería (🔋) y Almacenamiento Interno (💾).
- **Lector RSS Integrado**: Nueva área de noticias cargada mediante `feedparser` y `requests` para mantenerse al tanto de actualizaciones.
- **Dimensiones Fijas y Optimizadas**: Ventana ajustada a 864x600 con maximización deshabilitada para garantizar la integridad del diseño.
- **Mejoras Estéticas**: Alineación de etiquetas de app activa al margen izquierdo y títulos de sección claros para cada grupo de herramientas.

## [v3.2] - 2024-02-02
### ✨ Novedades
- **Gestor de Aplicaciones Completo**: Nueva pestaña dedicada para listar, buscar y filtrar todas las aplicaciones del dispositivo (Usuario y Sistema).
- **Monitor de Rendimiento**: Gráfico en tiempo real (0-100%) para supervisar la salud del dispositivo.
- **Monitor de Procesos**: Visualiza en tiempo real el consumo de CPU y RAM de cada proceso activo mediante la ventana de monitoreo (actualización ultra-robusta).
- **Noticias AdbAppDroid**: Marquesina interactiva con las últimas novedades del blog del desarrollador.
- **Logs de Actividad**: Consulta el archivo `activity_log.txt` para auditar todas las acciones realizadas durante la sesión.
- **Grabar Pantalla**: Captura videos de alta calidad directamente a tu almacenamiento local.
- **Identificación Visual por Iconos**: Ahora la aplicación extrae y muestra los iconos originales de las apps directamente desde el dispositivo utilizando `unzip`.
- **Caché Local de Iconos**: Sistema de almacenamiento local para carga instantánea de iconos previamente extraídos.
- **Optimización de Rendimiento**: Implementación de una cola de procesamiento secuencial ("Worker Queue") para la extracción de iconos, eliminando congelamientos de la UI.
- **Estandarización de Interfaz**: Refactorización a una interfaz basada en pestañas y estandarización cromática de botones de acción.
- **Seguridad UI**: El botón de desinstalación ahora destaca visualmente en rojo por seguridad.
- **Arquitectura Modular**: Refactorización del código monolítico a un paquete organizado (`adbappkiller/`).
- **Controladores Separados**: Lógica de ADB y descargas aislada de la capa de presentación.
- **Instalación Automática**: Sistema robusto para configurar `platform-tools` y `scrcpy` localmente.
- **Historial de Conexiones**: Persistencia de IPs y puertos utilizados anteriormente, permitiendo una reconexión rápida mediante un menú desplegable.
- **Limpieza de Datos de Panel**: Nuevo icono 🧹 en el panel de conexión para limpiar rápidamente los campos de entrada y el historial almacenado (con confirmación).
- **Captura y Grabación de Pantalla**: Funcionalidad nativa para tomar capturas de pantalla (`.png`) y grabar video (`.mkv`) directamente desde la interfaz.
- **Detección Inteligente de Audio**: Solo intenta grabar audio en dispositivos con Android 11+ (SDK 30+) para máxima estabilidad.
- **Compatibilidad Extrema (Xiaomi/Samsung)**: Uso forzado de **Software Encoders** (H.264/AAC) y resolución **720p** para garantizar que la grabación funcione incluso en dispositivos HyperOS/Android 15 con encoders de hardware inestables.
- **Robustez de Grabación**: Uso del contenedor MKV para asegurar que los videos sean reproducibles incluso tras cierres inesperados, con un periodo de cierre gracioso de 10 segundos.
- **Configuración de Salida**: Botón ⚙️ para establecer una carpeta de destino persistente para todos los medios generados.

## [v3.1] - Anterior
### 🚀 Características
- Versión monolítica totalmente funcional.
- Detección de aplicaciones en tiempo real.
- Funciones básicas de gestión: Desinstalar, Extraer APK, Limpiar datos.
- Identificación de aplicaciones de sistema vs usuario.
- Listado de permisos peligrosos.

## [v3.0] - Inicial
### 🛠 Base
- Implementación básica de comandos ADB mediante `subprocess`.
- GUI inicial con Tkinter.
- Soporte para desinstalación de paquetes.

---

### 📌 Próximas Versiones (Roadmap)
- [ ] Soporte para múltiples dispositivos conectados simultáneamente.
- [ ] Explorador de archivos remoto (Android -> PC).
- [ ] Registro de logs en tiempo real (`logcat` integrado).
- [ ] Tema oscuro/claro seleccionable por el usuario.
- [ ] Soporte multilingüe (Español/Inglés).

---

> [!NOTE]
> El versionado sigue el esquema `vMajor.Minor`. Los parches menores se documentarán dentro de cada versión.
