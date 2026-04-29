# Documentación de AdbAppDroid v5.0

Bienvenido a la documentación oficial de **AdbAppDroid**. Este proyecto es una herramienta potente y portable diseñada para gestionar aplicaciones en dispositivos Android a través de la interfaz ADB (Android Debug Bridge), con soporte multi-dispositivo e integración de scrcpy para espejo de pantalla.

## 📋 Índice

- [Guía de Instalación y Ejecución](INSTALLATION.md)
- [Estructura del Proyecto](STRUCTURE.md)
- [Guía de Migración](MIGRATION.md)
- [Control de Cambios y Versiones](CHANGELOG.md)
- [Mejoras Futuras](IMPROVEMENTS.md)

## 🚀 Propósito del Proyecto

AdbAppDroid v5.0 permite a los usuarios:
- **Soporte Multi-Dispositivo**: Gestiona múltiples terminales conectados simultáneamente.
- **Selector Activo**: Interfaz con menú desplegable para alternar el control entre dispositivos.
- **Rediseño Horizontal**: Nueva disposición optimizada con logs a la izquierda y controles a la derecha.
- **Encabezado Inteligente**: Información de hardware, batería (🔋) y almacenamiento (💾) en tiempo real.
- **Lector RSS**: Mantente informado con el feed de noticias integrado.
- **Detección Automática**: Identifica la app en primer plano en tiempo real.
- **Gestor Completo**: Pestaña dedicada para listar y buscar todas las apps del sistema.
- **Identificación Visual**: Extracción de iconos originales directamente desde el dispositivo.
- **Acciones Rápidas**: Desinstalar, Desactivar (bloatware), Extraer APK y Limpiar datos.
- **Captura y Grabación**: Toma de screenshots y grabación de pantalla con guardado automático.
- **Espejo de Pantalla**: Integración con `scrcpy` para control remoto desde la PC.

## 🛠 Tecnologías Utilizadas

- **Lenguaje**: Python 3.12+
- **GUI**: CustomTkinter (Interfaz moderna con soporte de temas).
- **Procesamiento de Imagen**: Pillow (PIL) para la gestión de iconos.
- **Herramientas**:
    - [ADB](https://developer.android.com/studio/releases/platform-tools) (Platform Tools).
    - [scrcpy](https://github.com/Genymobile/scrcpy) (Screen Copy).


## 👤 Desarrollador

Desarrollado por **QWERTY-ASERTY**.
Sitio web: [https://qwertyaserty.com/](https://qwertyaserty.com/)
Blog: [Rider Blog](https://ridersoportetecnico.blogspot.com/)

---

> [!NOTE]
> Esta herramienta está enfocada en la portabilidad y facilidad de uso para técnicos y entusiastas de Android.
