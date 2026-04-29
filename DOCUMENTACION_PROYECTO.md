# Documentación General de Cambios - AdbAppDroid

Esta documentación detalla la evolución técnica y estética del proyecto, consolidando todas las mejoras, nuevas funcionalidades y refinamientos de interfaz realizados para convertir AdbAppDroid en una herramienta de nivel profesional.

---

## 📱 Soporte Multi-Dispositivo Simultáneo (v5.0 - 2026)
Esta versión marca un hito en la escalabilidad del proyecto, permitiendo la gestión de múltiples dispositivos Android conectados al mismo tiempo (USB y WiFi).

- **Selector de Dispositivo (Active Device Selector)**: 
  - Nueva interfaz con un `CTkOptionMenu` en la cabecera que lista todos los dispositivos con estado `device`.
  - Cambio dinámico de contexto: Al cambiar de dispositivo en el menú, toda la interfaz (info de app, permisos, métricas) se actualiza instantáneamente para reflejar el estado del nuevo dispositivo seleccionado.
- **Arquitectura de Comandos por Serial**:
  - Refactorización completa del núcleo `ADBController`. Ahora todos los métodos de gestión (Desinstalar, Congelar, Limpiar Datos, Extraer APK, etc.) requieren y utilizan el `serial` específico, eliminando conflictos de ejecución.
- **Espejo y Grabación Multitarea**:
  - Soporte para **múltiples ventanas de Scrcpy simultáneas**. Ahora es posible abrir el espejo del Dispositivo A y el Dispositivo B al mismo tiempo.
  - Gestión de procesos mediante diccionarios indexados por `serial`, permitiendo grabar un dispositivo mientras se visualiza otro sin interferencias.
- **Monitorización Inteligente**:
  - El hilo de detección de dispositivos (`device_monitor`) ahora gestiona la lista de conexiones en tiempo real sin interrumpir la sesión activa.
  - Reconexión automática visual: Si el dispositivo seleccionado se desconecta, el sistema alterna automáticamente al siguiente disponible.

---

## 🚀 Actualización v4.5 (Smart Marquee & Persistence 2026)
Esta versión introduce una marquesina inteligente con desplazamiento infinito y una lógica de persistencia para contenidos críticos, asegurando que la información de mayor valor esté siempre visible.

---

## 📈 Monitoreo de Alto Rendimiento (v4.4)
- **Normalización de CPU (0-100%)**: Se implementó una lógica avanzada que calcula el uso real de la CPU basándose en el porcentaje "Idle" del kernel. Esto garantiza que dispositivos multi-núcleo (como el S23) muestren una escala real de 0 a 100% en lugar de valores acumulados (ej. 800%).
- **Gráfico de Rendimiento**: Visualización dinámica tipo "Scrolling Chart" con grid métrico y picos de consumo en tiempo real.
- **Motor de Procesos Ultra-Robusto**: Nuevo sistema de parseado de cabeceras dinámicas para el comando `top`. Se adapta automáticamente a variaciones de formato en diferentes versiones de Android (ej. manejo de columnas pegadas como `S[%CPU]`) y cuenta con *fallback* a `ps -A`.

### ⚠️ Nota sobre Interpretación de Valores de CPU
Existe una diferencia técnica necesaria entre el Monitor de Procesos y el Gráfico de Rendimiento:
- **Monitor de Procesos (% por Núcleo)**: Muestra valores *sin normalizar*. En Android, el 100% representa el uso total de **un solo núcleo**. En dispositivos multi-core, la suma total puede superar el 100% (ej: hasta 800% en 8 núcleos). Es normal ver que el proceso `top` consume ~25% de un núcleo mientras se ejecuta.
- **Gráfico de Rendimiento (Carga Total)**: Muestra el uso *normalizado* del sistema (0-100%). Representa la carga real sobre la capacidad total del procesador, calculada mediante el porcentaje *Idle* del kernel.

---

## 📰 Sistema de Noticias RSS: Smart Marquee (v4.5)
El feed RSS ha evolucionado de un simple widget a una marquesina inteligente (Smart Marquee) con las siguientes capacidades:
- **Desplazamiento Infinito (Seamless)**: Rediseño del motor de scroll para eliminar huecos vacíos. El contenido se repite dinámicamente para ofrecer un flujo de información ininterrumpido.
- **Lógica de Prioridad y Persistencia**:
  - **Último Post**: Identificación automática del post más reciente, presentado con el prefijo `ÚLTIMO POST:` y limpieza de etiquetas para una lectura fluida.
  - **Contenido Destacado Persistente**: Los posts marcados como `[DESTACADO]` tienen garantizada su presencia en la rotación, independientemente de la frecuencia de actualización del feed.
  - **Relleno Dinámico**: Si el volumen de destacados es bajo, el sistema completa la marquesina con los posts más recientes para mantener la interfaz activa.
- **Carga Garantizada**: Implementación de un cargador dual (`requests` + `urllib`) que utiliza la pila SSL del sistema para bypass de errores de certificados.
- **Interactividad**: Al hacer clic en la marquesina, se abre automáticamente el portal del desarrollador en el navegador predeterminado.

---


- **Fondo Desaturado y Profundidad**: Transición de negro puro a un azul grisáceo profesional (`#0F1117`) con tarjetas elevadas (`#161B22`).
- **Acentos y Semántica de Colores**: 
  - Azul Moderno / Índigo (`#3B82F6` / `#6366F1`) para acciones regulares (Espejo, Limpiar Datos).
  - Rojo Suave (`#EF4444`) estrictamente reservado para acciones destructivas (Desinstalar).
  - Verde Esmeralda (`#10B981`) para estados de éxito y permisos otorgados.
- **Tipografía y Geometría**: Implementación completa de la fuente `Roboto`. Redondeos consistentes de `12px` en contenedores y `8px` en botones.
- **Micro-interacciones**: Efectos *hover* con brillo incrementado en todos los componentes interactivos.
- **Diálogos Nativos Mejorados**: Las ventanas de alerta ahora lucen un texto rojo suave (`#FCA5A5`) y un ícono naranja corporativo (`#F59E0B`).

---

- **Log Vertical Extendido**: El panel de información de aplicaciones (izquierda) ahora aprovecha el 100% de la altura vertical de la ventana, facilitando la lectura de logs y permisos sin distracciones.

---

## 📊 Módulo: Monitor de Procesos
Se implementó una herramienta de supervisión en tiempo real integrada.
- **Ventana Independiente**: Creada con el patrón **Singleton** para evitar múltiples instancias abiertas.
- **Datos en Tiempo Real**: Muestra PID, Usuario, % CPU, Memoria RAM y Nombre del proceso mediante el comando `adb shell top`.
- **Refresco Automático**: Un hilo dedicado actualiza la información cada segundo sin bloquear la interfaz.

---

## 📦 Gestión Avanzada de Aplicaciones
- **Desglose de Permisos**: La lógica se mejoró para diferenciar entre permisos **Solicitados** y **Otorgados**.
- **Indicadores Visuales**:
  - ✅ **Verde**: Permisos activos.
  - ❌ **Gris**: Permisos no otorgados.
  - ⚠️ **Rojo**: Resaltado automático de permisos de alta peligrosidad (SMS, Ubicación, etc.).
- **Advertencias de Sistema**: Diálogos personalizados de advertencia al intentar desinstalar o desactivar aplicaciones críticas del sistema Android.

---

- **Identidad Visual**: Título personalizado `(SCRCPY - AdbAppDroid)` e integración del icono del programa mediante la API Win32.
- **Robustez y Audio (v3.6)**: 
  - **Lógica Centralizada**: Ejecución protegida mediante `--serial` para evitar conflictos en entornos multi-dispositivo.
  - **Streaming de Audio Avanzado**: Uso de **Raw PCM** y buffers optimizados para solucionar errores de inicialización de audio (WASAPI) en el PC.
  - **Registro de Errores**: Sistema de persistencia en `cache/scrcpy_error.log` para diagnóstico rápido.

---

## 🧠 Reconocimiento Dinámico de CPU (v4.3)
- **Eliminación de Diccionarios Estáticos**: El sistema ya no depende de un diccionario manual (`CHIPSET_MAP`) que requería actualizaciones constantes para nuevos procesadores.
- **Detección Directa**: Ahora extrae el nombre técnico de la plataforma o el modelo del SoC directamente desde las propiedades internas del dispositivo Android (`ro.soc.model`, `ro.board.platform`, `ro.hardware`).
- **Respaldo Inteligente**: En caso de que las propiedades del sistema no estén disponibles o sean ilegibles, el sistema cuenta con un método de respaldo (fallback) que analiza directamente el archivo `/proc/cpuinfo` para garantizar que la información de la CPU siempre se muestre, adaptándose universalmente a cualquier dispositivo que se conecte (ej. Snapdragon 8 Elite, procesadores genéricos, etc.).

---

## ⚙️ Sincronización y Registro (Logs)
- **Sincronización de Rutas**: Todas las funciones de exportación (Informes, Extracción de APK, Instalación) utilizan ahora la ruta definida por el usuario en el botón de ajustes (⚙️).
- **Log General de Actividad**: Se genera un archivo `activity_log.txt` en la raíz que registra:
  - Conexiones y desconexiones.
  - Apps detectadas en primer plano.
  - Todas las acciones de gestión ejecutadas.
  - Uso del sistema de ayuda.

---

## ℹ️ Sistema de Ayuda y Soporte
- **Botón de Información**: Nuevo icono `ℹ️` en la cabecera que abre la documentación.
- **Guía HTML Premium**: Creación de `help.html` con un diseño vanguardista, totalmente responsivo y con guías detalladas sobre el uso del aplicativo.

---

## 🛠️ Tecnologías y Dependencias Principales
- **GUI**: `customtkinter` (Python)
- **Motor ADB**: `adbutils`
- **Utilidades**: `subprocess`, `threading`, `ctypes` (para APIs de Windows), `webbrowser`.
- **Mirroring**: `scrcpy` core.

---
**Generado por Antigravity para QWERTY-ASERTY**
