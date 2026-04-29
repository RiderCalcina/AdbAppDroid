# Análisis de Nivel de Control mediante ADB (Android Debug Bridge)

Este documento detalla el alcance y nivel de control que la herramienta **AdbAppDroid** (y su módulo `adb_controller.py`) posee sobre un dispositivo Android cuando se conecta a través del modo de Depuración (USB o Inalámbrica).

## Alcance del Control (Privilegios de Interfaz)

La aplicación aprovecha los privilegios del entorno `shell` (ADB Debugging) para realizar acciones avanzadas que una aplicación normal instalada en el dispositivo Android **no podría ejecutar bajo ninguna circunstancia**. A través de la interfaz, el nivel de control se considera de **alta administración y gestión del sistema**.

A continuación, se desglosa lo que la interfaz puede controlar actualmente según su código fuente:

### 1. Gestión Profunda de Aplicaciones
- **Desinstalación Forzada**: Capacidad para desinstalar tanto aplicaciones instaladas por el usuario como aplicaciones del sistema integradas (bloatware) mediante `pm uninstall`.
- **Congelación de Aplicaciones**: Posibilidad de desactivar (congelar) aplicaciones del sistema mediante el comando `pm disable-user`, impidiendo completamente su ejecución sin borrarlas.
- **Limpieza Absoluta**: Borrar de forma instantánea todos los datos de usuario y la memoria caché de cualquier aplicación mediante `pm clear`.
- **Extracción de Paquetes**: Extraer y copiar los archivos originales de instalación (`.apk`) de las aplicaciones del teléfono hacia la computadora mediante la función `adb pull`.
- **Instalación Silenciosa**: Instalar archivos APK locales en el dispositivo en segundo plano (`pm install -r`), omitiendo las pantallas de confirmación habituales de Android.

### 2. Control de Pantalla y Multimedia
- **Capturas de Pantalla Invisibles**: Tomar capturas de la pantalla (`screencap`) y transferirlas a la computadora sin mostrar advertencias visuales o de sonido en el propio dispositivo.
- **Grabación Oculta**: Grabar en video la pantalla del usuario en segundo plano (usando la herramienta `scrcpy` con el parámetro `--no-window`), capturando también el **audio interno** del sistema y las aplicaciones operativas.
- **Control en Tiempo Real**: Visualizar y controlar remotamente la pantalla del dispositivo ("Espejo") desde la PC.

### 3. Monitoreo y Lectura del Sistema
- **Análisis de Hardware**: Leer información técnica detallada del dispositivo, incluyendo uso de memoria RAM, procesador, estado de la batería, resolución nativa de pantalla y almacenamiento en uso.
- **Seguimiento de Actividad**: Conocer, detectar y registrar qué aplicación exacta está siendo utilizada por el usuario en primer plano en todo momento mediante `dumpsys window`.

## Limitaciones (Frontera Root)

Es importante recalcar que, aunque el nivel de control es asombrosamente alto, ADB opera bajo el usuario `shell` (normalmente UID 2000). **Esto no equivale a tener permisos Root (Superusuario / UID 0)**.

**Lo que la herramienta no puede hacer (Sin Root):**
- Modificar libremente los binarios o bibliotecas dentro de la partición de solo lectura `/system` del núcleo de Android.
- Acceder a los directorios de datos privados de otras aplicaciones (como bases de datos de mensajes locales en `/data/data/`, a menos que se use un comando de backup global).
- Modificar el sistema en un nivel crítico (como cambiar el kernel).

Aun así, para los propósitos de **administración, gestión operativa, auditoría de pantalla y control de aplicaciones**, AdbAppDroid tiene un **control casi total y altamente privilegiado** sobre el dispositivo destino.
