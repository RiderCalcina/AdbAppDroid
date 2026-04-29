# AdbAppDroid v5.0
## Manual de Usuario Oficial

![AdbAppDroid Logo](https://qwertyaserty.com/assets/img/logo.png) <!-- Nota: Placeholder del logo -->

**Gestión avanzada de dispositivos Android desde Windows (Multi-Dispositivo)**

**Desarrollador:** QWERTY-ASERTY  
**Versión:** 5.0  
**Año:** 2026  

---

## ⚖️ Página de derechos de autor / Legal
**Copyright © 2026 QWERTY-ASERTY**  
*Reservados todos los derechos.*

### Aviso Legal y Descargo de Responsabilidad
Este software se proporciona "tal cual", sin garantías de ningún tipo. El uso de herramientas ADB para modificar aplicaciones del sistema o configuraciones avanzadas de Android puede anular la garantía de su dispositivo o causar inestabilidad. QWERTY-ASERTY no se hace responsable de daños derivados del uso incorrecto de esta herramienta.

*   **Licencia:** Uso personal y profesional bajo licencia de QWERTY-ASERTY.
*   **Marcas:** Android y ADB son marcas registradas de Google LLC.
*   **Contacto:** [soporte@qwertyaserty.com](mailto:soporte@qwertyaserty.com)

---

## 📋 Tabla de contenidos
1.  [Introducción / Bienvenida](#-introducción--bienvenida)
2.  [Requisitos del sistema](#-requisitos-del-sistema)
3.  [Instalación](#-instalación)
4.  [Guía de inicio rápido](#-guía-de-inicio-rápido)
5.  [Uso principal / Funcionalidades clave](#-uso-principal--funcionalidades-clave)
6.  [Tareas avanzadas](#-tareas-avanzadas)
7.  [Solución de problemas](#-solución-de-problemas)
8.  [Preguntas frecuentes (FAQ)](#-preguntas-frecuentes-faq)
9.  [Actualizaciones y mantenimiento](#-actualizaciones-y-mantenimiento)
10. [Glosario](#-glosario)
11. [Contacto y soporte](#-contacto-y-soporte)

---

## 👋 Introducción / Bienvenida
¡Bienvenido a **AdbAppDroid v5.0**! Esta aplicación es una solución integral y potente diseñada para facilitar la interacción entre tu PC con Windows y tus dispositivos Android mediante el protocolo ADB (Android Debug Bridge).

### Propósito y Beneficios
AdbAppDroid elimina la complejidad de la línea de comandos de ADB, ofreciendo una interfaz gráfica moderna que permite gestionar múltiples aplicaciones, monitorizar recursos y realizar espejado de pantalla con un solo clic.

---

## 💻 Requisitos del sistema
*   **Sistema Operativo:** Windows 10, 11 (64-bit recomendado).
*   **Procesador:** Intel Core i3 o superior / AMD equivalente.
*   **RAM:** 4 GB mínimo (8 GB recomendados para fluidez en Scrcpy).
*   **Espacio en disco:** 200 MB libres.
*   **Dependencias:**
    *   ADB Platform-Tools (incluidas en el paquete).
    *   Controladores USB del fabricante del dispositivo.

---

## ⚙️ Instalación
### Descarga y Ejecución
1.  Descarga el paquete oficial desde [qwertyaserty.com](https://qwertyaserty.com).
2.  Ejecuta el paquete de instalación.
3.  Ejecuta el archivo `AdbAppDroid.exe` (el ejecutable principal).

---

## 🚀 Guía de inicio rápido
Para que puedas empezar a utilizar AdbAppDroid de inmediato, sigue estos pasos detallados:

1.  **Habilitar el modo de desarrollador en Android:**
    *   En tu dispositivo móvil, dirígete a **Ajustes > Información del dispositivo**.
    *   Busca la opción **Número de compilación** y púlsala repetidamente (normalmente 7 veces) hasta que aparezca el mensaje "¡Ya eres desarrollador!".
    *   Regresa al menú principal de Ajustes, entra en **Sistema > Opciones de desarrollador** (o busca "Opciones de desarrollador" directamente).
    *   Activa la casilla **Depuración USB**. Si el dispositivo te pide confirmación, acepta.

2.  **Preparación del PC:**
    *   Asegúrate de que los controladores (drivers) USB de tu fabricante estén instalados.
    *   Conecta el dispositivo móvil al PC mediante un cable USB de alta calidad.

3.  **Primer contacto y autorización:**
    *   Al conectar el dispositivo, aparecerá un mensaje en la pantalla del móvil preguntando **"¿Permitir depuración USB?"**. Marca la casilla "Permitir siempre desde este ordenador" y pulsa **Aceptar**. Este paso es crucial para que AdbAppDroid pueda comunicarse con el móvil.

4.  **Selección de Dispositivo:**
    *   Abre **AdbAppDroid.exe**.
    *   Si tienes varios dispositivos conectados, utiliza el **menú desplegable** en la barra superior para elegir cuál deseas controlar. Toda la interfaz se adaptará instantáneamente.
    *   Para usarlo sin cables, asegúrate de estar en la misma red Wi-Fi, obtén la IP de tu móvil y pulsa el botón de conexión WiFi en la app.

5.  **Verificación Final:**
    *   Una vez seleccionado, verás el nombre y estado de tu dispositivo en la barra superior. ¡Ya puedes empezar a gestionar tus apps o usar el monitor de procesos!

---


## 🛠️ Uso principal / Funcionalidades clave

### 1. Gestión de Aplicaciones
*   **Lista de Apps:** Visualiza aplicaciones de usuario y de sistema por separado.
*   **Desinstalar/Desactivar:** Elimina apps no deseadas. ⚠️ *Aviso: AdbAppDroid mostrará una advertencia al intentar modificar apps críticas del sistema.*
*   **Limpiar Datos:** Resetea apps al estado inicial.

### 2. Extracción de APKs
Selecciona cualquier aplicación instalada y haz clic en "Extraer". El programa guardará el archivo `.apk` directamente en tu carpeta configurada.

### 3. Espejo de Pantalla Simultáneo (Scrcpy)
Activa el modo "Mirror" para ver e interactuar con la pantalla de tus móviles. Puedes abrir múltiples ventanas de espejo al mismo tiempo para diferentes dispositivos seleccionados.

### 4. Conexión WiFi
Escribe la IP de tu dispositivo y el puerto para gestionar tu móvil sin necesidad de cables.

---

## 🚀 Tareas avanzadas
*   **Monitor de Procesos:** Visualiza en tiempo real el consumo de CPU y RAM de cada proceso activo mediante la ventana de monitoreo.
*   **Logs de Actividad:** Consulta el archivo `activity_log.txt` para auditar todas las acciones realizadas durante la sesión.
*   **Grabar Pantalla:** Captura videos de alta calidad directamente a tu almacenamiento local.

---

## ❓ Solución de problemas
*   **Dispositivo no detectado:** Verifica los controladores USB o cambia el cable. Asegúrate de que la depuración USB esté activa.
*   **Error WiFi:** Ambos dispositivos deben estar en la misma red local.
*   **Permiso denegado:** Algunas funciones requieren autorización explícita en la pantalla del móvil al primer uso.

---

## 💬 Preguntas frecuentes (FAQ)
*   **¿Root?** No, funciona en dispositivos no rooteados.
*   **¿Android 14+?** Sí, soporta todas las versiones modernas.
*   **¿Puedo controlar varios móviles a la vez?** Sí, con la v5.0 puedes alternar entre ellos con el selector superior y abrir múltiples espejos Scrcpy.
*   **¿Por qué el porcentaje de CPU es diferente en la lista y en el gráfico?** La lista (Monitor de Procesos) muestra cuánto usa cada proceso por cada núcleo individual (donde 100% = 1 núcleo). El gráfico muestra el uso total del sistema (donde 100% = todos los núcleos juntos).

---

## 🔄 Actualizaciones y mantenimiento
Para buscar actualizaciones, visita la web oficial. 

---


## 📖 Glosario
*   **ADB:** Android Debug Bridge. Herramienta que permite la comunicación PC-Móvil.
*   **APK:** Formato de archivo para instalar aplicaciones en Android.
*   **Scrcpy:** Herramienta de alta velocidad para espejo de pantalla.

---

## 📞 Contacto y soporte
*   **Web:** [qwertyaserty.com](https://qwertyaserty.com)
*   **Correo:** [soporte@qwertyaserty.com](mailto:soporte@qwertyaserty.com)

---
*Generado automáticamente para el equipo de desarrollo de AdbAppDroid v5.0.*
