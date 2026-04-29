# Mejoras y Futuro del Proyecto

ADBAppKiller tiene un gran potencial de expansión. Esta sección documenta ideas y mejoras planificadas para futuras versiones.

## 🚀 Mejoras de Rendimiento
- **Caché Inteligente**: Implementar un sistema de caché más avanzado para las etiquetas de las aplicaciones y sus iconos, reduciendo las llamadas a ADB.
- **Asincronía Total**: Migrar más llamadas de bloqueo a hilos secundarios o usar `asyncio` para que la UI nunca se sienta pesada.

## ✨ Nuevas Funcionalidades
1. **Gestor de Archivos (File Explorer)**:
   - Capacidad para arrastrar y soltar archivos entre la PC y el dispositivo.
   - Navegación por carpetas `/sdcard/`.
2. **Instalación Múltiple**:
   - Seleccionar varios archivos APK en la PC e instalarlos todos en lote (batch install).
3. **Logcat Viewer**:
   - Una ventana dedicada para ver los logs del sistema Android en tiempo real, con filtros por prioridad y etiqueta.
4. **Captura de Pantalla Avanzada**:
   - Botón dedicado para tomar capturas de pantalla y guardarlas automáticamente en una carpeta local con fecha y nombre de la app.
5. **Comandos Personalizados**:
   - Una "consola rápida" para enviar comandos ADB personalizados sin salir de la herramienta.

## 🎨 Diseño y Experiencia de Usuario
- **Soporte para Temas**: Cargar archivos `.json` de temas para que el usuario personalice los colores.
- **Iconos de Apps**: Mostrar el icono real de la aplicación activa extraído del APK.
- **Notificaciones Nativas**: Usar notificaciones de Windows para avisar cuando una desinstalación o descarga ha finalizado.

## 🌐 Conectividad
- **ADB over Wi-Fi**: Facilitar la conexión inalámbrica guiando al usuario para emparejar el dispositivo sin cables.
- **Soporte Multi-dispositivo**: Selector/Dropdown para cambiar entre varios teléfonos conectados a la misma PC.

---

### 🤝 Contribuciones
Si tienes ideas adicionales o encuentras errores, no dudes en reportarlos a través de los canales oficiales en [qwertyaserty.com](https://qwertyaserty.com/).

---

> [!NOTE]
> Estas mejoras se priorizarán según el feedback de los usuarios y la utilidad general para el soporte técnico.
