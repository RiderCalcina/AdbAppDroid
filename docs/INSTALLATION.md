# Guía de Instalación y Ejecución

Esta guía detalla los pasos necesarios para configurar y ejecutar ADBAppKiller en una nueva computadora.

## 📋 Requisitos Previos

- **Sistema Operativo**: Windows 10 o superior (64 bits recomendado).
- **Python**: Versión 3.8 o superior instalada.
    - Puedes descargarlo desde [python.org](https://www.python.org/downloads/).
    - **IMPORTANTE**: Asegúrate de marcar la casilla "Add Python to PATH" durante la instalación.

## ⚙️ Instalación

1. **Descargar el proyecto**:
   Clona el repositorio o descarga el archivo ZIP y extráelo en una carpeta de tu elección.

2. **Instalación de Dependencias**:
   ADBAppKiller está diseñado para usar únicamente la biblioteca estándar de Python (Tkinter), por lo que en la mayoría de los casos no requiere instalar paquetes adicionales mediante `pip`.

3. **Configuración de Herramientas (ADB y scrcpy)**:
   El programa incluye un sistema de instalación automática:
   - Al ejecutar la aplicación por primera vez, si no detecta las carpetas `platform-tools` o `scrcpy` en el directorio raíz, aparecerán botones en la interfaz para descargarlos e instalarlos automáticamente.
   - Alternativamente, puedes colocar manualmente las carpetas `platform-tools` (con `adb.exe`) y `scrcpy` (con `scrcpy.exe`) en el directorio principal del proyecto.

## 🚀 Ejecución

Para iniciar la aplicación, abre una terminal (CMD o PowerShell) en la carpeta del proyecto y ejecuta:

```powershell
python main.py
```

También puedes simplemente hacer doble clic en el archivo `main.py` si tienes los archivos `.py` asociados con el intérprete de Python.

## 📱 Preparación del Dispositivo Android

Para que la herramienta funcione, tu dispositivo Android debe tener:
1. **Opciones de Desarrollador** activadas.
2. **Depuración USB** activada.
3. Conectado a la PC mediante un cable USB de buena calidad.
4. Al conectar, acepta la ventana emergente en el teléfono que pide "Permitir depuración USB" (se recomienda marcar "Permitir siempre desde esta computadora").

---

> [!TIP]
> Si la herramienta no detecta el dispositivo, intenta cambiar el puerto USB o el cable, y asegúrate de que el driver ADB de tu fabricante está instalado.
