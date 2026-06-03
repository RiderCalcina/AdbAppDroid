# AdbAppDroid v5.1
## Manual de Usuario Oficial

![AdbAppDroid Logo](https://qwertyaserty.com/assets/img/logo.png) <!-- Nota: Placeholder del logo -->

**Gestión avanzada de dispositivos Android desde Windows (Multi-Dispositivo & Split APKs)**

**Desarrollador:** QWERTY-ASERTY  
**Versión:** 5.1  
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
6.  [Gestión Avanzada de APKs y Split Bundles](#-gestión-avanzada-de-apks-y-split-bundles)
7.  [Tareas avanzadas](#-tareas-avanzadas)
8.  [Solución de problemas](#-solución-de-problemas)
9.  [Preguntas frecuentes (FAQ)](#-preguntas-frecuentes-faq)
10. [Actualizaciones y mantenimiento](#-actualizaciones-y-mantenimiento)
11. [Glosario](#-glosario)
12. [Contacto y soporte](#-contacto-y-soporte)

---

## 👋 Introducción / Bienvenida
¡Bienvenido a **AdbAppDroid v5.1**! Esta aplicación es una solución integral y potente diseñada para facilitar la interacción entre tu PC con Windows y tus dispositivos Android mediante el protocolo ADB (Android Debug Bridge).

### Propósito y Beneficios
AdbAppDroid elimina la complejidad de la línea de comandos de ADB, ofreciendo una interfaz gráfica moderna que permite gestionar múltiples aplicaciones, monitorizar recursos y realizar espejado de pantalla con un solo clic.

---

## 💻 Requisitos del sistema
*   **Sistema Operativo:** Windows 10, 11 (64-bit recomendado).
*   **Procesador:** Intel Core i3 o superior / AMD equivalente.
*   **RAM:** 4 GB mínimo (8 GB recomendados para fluidez en Scrcpy).
*   **Espacio en disco:** 200 MB libres.
*   **Dependencias:**
    *   ADB Platform-Tools (incluidas localmente en el paquete).
    *   Controladores USB del fabricante del dispositivo.

---

## ⚙️ Instalación
### Descarga y Ejecución
1.  Descarga el paquete oficial desde [qwertyaserty.com](https://qwertyaserty.com).
2.  Ejecuta el paquete de instalación.
3.  Inicia la aplicación ejecutando `main.py` o el acceso directo de `AdbAppDroid.exe`.

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
    *   Abre **AdbAppDroid**.
    *   Si tienes varios dispositivos conectados, utiliza el **menú desplegable** en la barra superior para elegir cuál deseas controlar. Toda la interfaz se adaptará instantáneamente.

5.  **Emparejamiento y Conexión Inalámbrica (Android 11+):**
    *   Haz clic en el enlace azul **"Emparejar dispositivo nuevo"** en la sección Wi-Fi de la interfaz.
    *   Activa la **Depuración Inalámbrica** en tu celular, entra a "Emparejar dispositivo con código" y copia la Dirección IP, el Puerto de emparejamiento y el Código de 6 dígitos en el popup modal flotante (`CTkPairingDialog`) del programa.
    *   Tras emparejarse con éxito, ingresa la IP y el Puerto de conexión habituales de la pantalla de Depuración Inalámbrica de tu celular y presiona **Conectar**. El terminal inalámbrico se añadirá a la lista de dispositivos activos en el desplegable superior.

---

## 🛠️ Uso principal / Funcionalidades clave

### 1. Gestión de Aplicaciones
AdbAppDroid lee la app en primer plano y ofrece los siguientes controles directos:
*   **Desinstalar:** Elimina apps del móvil de forma directa. Para aplicaciones de sistema, muestra una advertencia de seguridad crítica y ejecuta un debloat de sistema desinstalándola de forma limpia para el usuario activo (`pm uninstall -k --user 0`).
*   **Desactivar (Congelar):** Inhabilita la ejecución y oculta la aplicación de la interfaz del móvil usando `pm disable-user --user 0` sin borrar sus archivos.
*   **Limpiar Datos:** Resetea apps al estado inicial borrando su caché y datos de usuario, con barra de progreso en vivo.
*   **Guardar Informe:** Exporta todos los metadatos y la lista de permisos ordenados del panel izquierdo en un archivo `.txt`.

### 2. Inspector de Seguridad y Permisos
El panel izquierdo audita dinámicamente la aplicación en pantalla:
*   Muestra los permisos activos con un check verde.
*   Muestra los permisos denegados o inactivos con una cruz roja y etiqueta `(Inactivo)`.
*   Resalta de forma destacada en color rojo los **Permisos Peligrosos** que comprometen la privacidad.

### 3. Espejo de Pantalla (Scrcpy)
Activa el modo "Mirror" (Espejo) para visualizar y controlar la pantalla de tus móviles. La ventana se ubica automáticamente a la derecha de la interfaz sin tapar tus controles. Soporta múltiples espejos en paralelo.

### 4. Control de Pantalla y Capturas
*   **Carpeta:** Configura el directorio donde se almacenarán las capturas y grabaciones.
*   **Capturar:** Toma una captura en formato `.png` de la pantalla actual.
*   **Grabar:** Graba video fluido en formato `.mkv` con soporte de audio interno y perfiles de compatibilidad específicos para dispositivos Xiaomi/HyperOS.

---

## 💾 Gestión Avanzada de APKs y Split Bundles

AdbAppDroid cuenta con soporte transparente para la manipulación y empaquetamiento de App Bundles (Split APKs):

### 1. Extracción Inteligente de Aplicaciones
Al presionar el botón **Extraer APK**:
- Si la aplicación consta de un único archivo, se descarga directamente en formato `.apk` en el ordenador.
- Si la aplicación es dividida (Split APK), el programa descarga progresivamente todas sus partes asociadas (base, idioma, recursos) y las empaqueta juntas en un archivo comprimido `.zip` instalable.

### 2. Instalación Universal (APK / XAPK / APKS / ZIP)
Al presionar **Instalar APK**, puedes elegir archivos estándar o empaquetados:
- **APK simples:** Instalación estándar mediante ADB.
- **Split APKs / Bundles:** Selecciona directamente archivos `.zip`, `.xapk` o `.apks`. El programa descomprimirá e instalará por lotes todas las partes necesarias mediante `adb install-multiple`.
- **Motor de Diagnóstico:** Si la instalación falla con el error `INSTALL_FAILED_MISSING_SPLIT`, la interfaz lo intercepta y aconseja al usuario desinstalar la versión existente del celular (de la Play Store) antes de reintentar la instalación del bundle.

---

## 🚀 Tareas avanzadas
*   **Monitor de Procesos:** Abre una ventana interactiva y ordenable que detalla el PID, nombre, RAM y consumo de CPU por núcleo de cada tarea activa en tu dispositivo.
*   **Gráfica de CPU:** Monitoreo dinámico continuo de la carga del dispositivo de 0 a 100%.
*   **Logs de Actividad:** Consulta el archivo `activity_log.txt` en la raíz del proyecto para auditar todas las operaciones.
*   **Marquesina RSS:** Marquesina integrada que lee novedades y actualizaciones de desarrollo desde `QwertyAserty.com`.

---

## ❓ Solución de problemas
*   **Dispositivo no detectado:** Verifica los controladores USB o cambia el cable. Asegúrate de que la depuración USB esté activa.
*   **Error WiFi:** Ambos dispositivos deben estar en la misma red local.
*   **Permiso denegado / Unauthorized:** Elimina las autorizaciones de depuración del PC en el menú de desarrollador de tu celular, vuelve a conectarlo y acepta el diálogo RSA.
*   **Error INSTALL_FAILED_MISSING_SPLIT:** Desinstala la app original en tu teléfono antes de intentar reinstalar el paquete APK/ZIP extraído.

---

## 💬 Preguntas frecuentes (FAQ)
*   **¿Root?** No, funciona en dispositivos no rooteados.
*   **¿Android 14+ / 15?** Sí, soporta todas las versiones modernas.
*   **¿Puedo controlar varios móviles a la vez?** Sí, puedes alternar entre ellos con el selector superior y abrir múltiples espejos en paralelo.

---

## 🔄 Actualizaciones y mantenimiento
Para buscar actualizaciones, visita la web oficial. 

---

## 📖 Glosario
*   **ADB:** Android Debug Bridge. Herramienta que permite la comunicación PC-Móvil.
*   **APK:** Formato de archivo para instalar aplicaciones en Android.
*   **Split APK:** Estructura modular de aplicaciones divididas en recursos específicos.
*   **Scrcpy:** Herramienta de alta velocidad para espejo de pantalla.

---

## 📞 Contacto y soporte
*   **Web:** [qwertyaserty.com](https://qwertyaserty.com)
*   **Correo:** [soporte@qwertyaserty.com](mailto:soporte@qwertyaserty.com)

---
*Generado para el equipo de desarrollo de AdbAppDroid v5.1.*
